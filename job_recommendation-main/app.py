import streamlit as st
import pandas as pd
import numpy as np
from PyPDF2 import PdfReader
import re
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet, stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from bs4 import BeautifulSoup
from io import BytesIO
import base64

def return_data_list():
    try:
        with open('WebCrawler/table_2025.html', 'r', encoding='utf-8') as f:
            contents = f.read()
        soup = BeautifulSoup(contents, 'html.parser')
        rows = soup.find_all('tr')

        job_data_list = []
        for row in rows:
            td_ele = row.find_all('td')
            if not td_ele:
                continue
            row_data = []
            for td in td_ele:
                a = td.find('a', href=True)
                if a and a.get('href'):
                    link = a['href']
                    if link.startswith("/"):
                        link = "https://github.com" + link
                    row_data.append(link)
                else:
                    row_data.append(td.text.strip())
            job_data_list.append(row_data)
        return job_data_list
    except Exception as e:
        st.error(f"Error parsing table.html: {e}")
        return []

def make_clickable(link):
    if not isinstance(link, str) or link.strip() == "":
        return ""
    link = link.strip()
    if link.startswith("/"):
        link = "https://github.com" + link
    if not link.startswith("http"):
        link = "https://" + link
    return f'<a href="{link}" target="_blank" rel="noopener noreferrer" style="color:#0078ff; text-decoration:none; font-weight:600;">Apply ↗</a>'

def read_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    page = reader.pages[0]
    return page.extract_text()

def keep_alpha_char(text):
    text = re.sub(r'[^a-zA-Z]', ' ', text)
    return re.sub(r'\s+', ' ', text)

def nltk_pos_tagger(nltk_tag):
    if nltk_tag.startswith('J'):
        return wordnet.ADJ
    elif nltk_tag.startswith('V'):
        return wordnet.VERB
    elif nltk_tag.startswith('N'):
        return wordnet.NOUN
    elif nltk_tag.startswith('R'):
        return wordnet.ADV
    else:
        return None

def lemmatize_sentence(sentence):
    wordnet_tagged = map(lambda x: (x[0], nltk_pos_tagger(x[1])), nltk.pos_tag(nltk.word_tokenize(sentence)))
    lemmatizer = WordNetLemmatizer()
    return " ".join(lemmatizer.lemmatize(word, tag) if tag else word for word, tag in wordnet_tagged)

def remove_stop_words(text):
    stop_words = set(stopwords.words('english'))
    return ' '.join(word for word in nltk.word_tokenize(str(text)) if word.lower() not in stop_words)

def pre_process_resume(resume_text):
    resume_text = keep_alpha_char(resume_text)
    resume_text = lemmatize_sentence(resume_text)
    resume_text = remove_stop_words(resume_text)
    return resume_text.lower()

def pre_process_data_job(job_df):
    job_df.dropna(subset=['Role'], inplace=True)
    job_df['data'] = job_df['Role'].apply(lambda x: remove_stop_words(lemmatize_sentence(keep_alpha_char(x))).lower())
    return job_df

def recommend_job(resume_text, tfidf_matrix, tfidf_vectorizer, df):
    resume_text_vector = tfidf_vectorizer.transform([resume_text])
    cosine_similarities = cosine_similarity(resume_text_vector, tfidf_matrix)
    job_indices = cosine_similarities.argsort()[0][::-1]
    return pd.DataFrame([df.iloc[i] for i in job_indices])

def return_table_job(resume_text, job_df):
    tfidf_vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf_vectorizer.fit_transform(job_df['data'])
    recommended_jobs = recommend_job(resume_text, tfidf_matrix, tfidf_vectorizer, job_df)
    recommended_jobs = recommended_jobs.drop(columns=recommended_jobs.columns[0])
    return recommended_jobs

def get_top_features(resume_text, job_df):
    tfidf_vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf_vectorizer.fit_transform(job_df['data'])
    resume_text_vector = tfidf_vectorizer.transform([resume_text])
    feature_names = np.array(tfidf_vectorizer.get_feature_names_out())
    feature_indices = np.argsort(resume_text_vector.toarray()[0])[::-1]
    return feature_names[feature_indices]

def get_job_df():
    data_list = return_data_list()
    job_df = pd.DataFrame(data_list, columns=['Company', 'Role', 'Location', 'Application/Link', 'Date Posted'])
    job_df = pre_process_data_job(job_df)
    return job_df

def post_process_table(uploaded_file, job_df):
    df_resume = return_table_job(str(uploaded_file), job_df)
    df_resume_sorted = df_resume.head(50).sort_index(ascending=True)
    df_resume_sorted['Application/Link'] = df_resume_sorted['Application/Link'].apply(make_clickable)
    df_resume_sorted = df_resume_sorted.iloc[:, :-1]
    df_resume_sorted = df_resume_sorted.reset_index(drop=True)
    df_resume_sorted.index = df_resume_sorted.index + 1
    return df_resume_sorted

def main():
    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger')
    nltk.download('wordnet')
    nltk.download('stopwords')
    st.markdown("""
        <style>
            /*  Make everything white */
            html, body, [class*="stAppViewContainer"], [class*="stApp"], [class*="block-container"], [data-testid="stSidebar"], [data-testid="stAppViewContainer"], [data-testid="stMain"] {
                background-color: white !important;
                color: black !important;
            }

            .block-container {
                padding: 1rem 3rem 3rem 3rem;
                max-width: 100% !important;
            }

            h1, h3 { text-align: center; }
            table { width: 100% !important; border-collapse: collapse !important; }
            th, td {
                text-align: left !important;
                padding: 10px !important;
                border: 1px solid #ddd !important;
                color: black !important;
            }
            th {
                background-color: #f9f9f9 !important;
                font-weight: bold;
            }
            .resume-box {
                background-color: #f0f0f0;
                color: black;
                padding: 15px;
                border-radius: 10px;
                margin-top: 20px;
                border: 1px solid #bdbdbd;
            }
            .download-btn {
                background-color: #d6d6d6;
                color: black !important;
                padding: 10px 18px;
                border-radius: 10px;
                text-align: center;
                font-weight: 600;
                text-decoration: none;
                border: none;
                transition: 0.3s ease;
                display: inline-block;
                margin: 20px 0;
            }
            .download-btn:hover { background-color: #bdbdbd; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div style="text-align:center; margin-bottom:25px;">
            <h1 style="font-weight:800; color:black; font-size:40px;"> Internship Recommendation System</h1>
            <h3 style="font-weight:600; color:black; font-size:22px;">
                Your next opportunity is just waiting to get matched with your resume 
            </h3>
        </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader("📄 Upload your Resume (PDF or TXT)", type=["pdf", "txt"])

    if uploaded_file:
        st.markdown(f"<div class='resume-box'><b>Uploaded File:</b> {uploaded_file.name}</div>", unsafe_allow_html=True)

        resume = read_pdf(uploaded_file)
        resume = pre_process_resume(resume)

        job_df = get_job_df()
        df_resume_sorted = post_process_table(resume, job_df)

        st.markdown("<h4 style='margin-top:20px; color:black;'>Top Skills Extracted from Resume:</h4>", unsafe_allow_html=True)
        top_keywords_df = pd.DataFrame(get_top_features(resume, job_df)[:5], columns=["Top Skills"])
        html_table = top_keywords_df.to_html(index=False, escape=False)
        st.markdown(f"""
        <div style="color:black; background-color:white; padding:10px; border:1px solid #ddd; border-radius:8px;">
        {html_table}
        </div>
        """, 
        unsafe_allow_html=True)

        csv_buffer = BytesIO()
        df_resume_sorted.to_csv(csv_buffer, index=False)
        b64 = base64.b64encode(csv_buffer.getvalue()).decode()
        href = f'<a class="download-btn" href="data:file/csv;base64,{b64}" download="recommended_jobs.csv"> ⬇ Download Matching Jobs CSV</a>'
        st.markdown(href, unsafe_allow_html=True)

        st.markdown("<h4 style='margin-top:30px; color:black;'>Recommended Internships:</h4>", unsafe_allow_html=True)
        st.write(df_resume_sorted.to_html(escape=False), unsafe_allow_html=True)

    st.markdown("<p style='text-align:center; margin-top:50px;'>© 2025 Smart Resume Matcher</p>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
