# 🧠 RecIntern — Intelligent Internship & Job Recommendation System  
  
**RecIntern** is an AI-powered system designed to recommend internships and job opportunities that best match a user’s skills and interests.  
The project uses **web scraping**, **machine learning**, and **NLP-based matching** to collect and analyze real-world data from multiple job portals.


---

## 🔍 Key Features  
- **Web Scraping Engine:** Collects fresh internship and job listings from Github Repository.  
- **Resume Skill Extraction:** Parses uploaded resumes and identifies technical and soft skills using NLP.  
- **Similarity Matching:** Compares user skills with scraped job descriptions to find the best matches.  
- **Simple Interface:** Allows users to view top internships and apply directly through scraped links.  

---

## 🧰 Tech Stack  
| Component | Technology |
|------------|-------------|
| **Programming Language** | Python |
| **Web Scraping** | BeautifulSoup, Requests, Selenium |
| **Data Processing** | Pandas, NumPy |
| **Machine Learning / NLP** | scikit-learn, spaCy |
| **Visualization / UI** | Streamlit / Flask |
| **Storage** | CSV / SQLite |

---

## ⚙️ How It Works  
1. **Data Collection via Scraping:**  
   - The scraper crawls selected internship/job websites and extracts titles, company names, descriptions, required skills, and links.  
   - Data is cleaned and stored in structured CSV format.  

2. **Skill Extraction:**  
   - User uploads their resume (PDF or text).  
   - NLP pipeline identifies and extracts skill keywords.  

3. **Matching Algorithm:**  
   - Uses cosine similarity between user skills and scraped job descriptions to compute relevance scores.  

4. **Recommendation Output:**  
   - Displays top 50 most relevant opportunities with links to apply.  

---
 
   ```bash
   python scraper.py
