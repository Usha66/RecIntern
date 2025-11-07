from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import os
import datetime
import webbrowser

os.makedirs("WebCrawler", exist_ok=True)

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless") 
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(options=chrome_options)

# GitHub Repo URL for 2025 internships
url = "https://github.com/SimplifyJobs/Summer2025-Internships"
driver.get(url)

try:
    article = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "markdown-body"))
    )
    article_html = article.get_attribute("outerHTML")
    soup = BeautifulSoup(article_html, "html.parser")
    table_tag = soup.find("table")

    if table_tag:
        styled_html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>2025 Internship Listings</title>
            <style>
                body {{
                    background-color: white;
                    color: black;
                    font-family: Arial, sans-serif;
                    margin: 30px;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    border: 1px solid black;
                }}
                th, td {{
                    border: 1px solid black;
                    padding: 8px;
                    text-align: left;
                }}
                th {{
                    background-color: #f2f2f2;
                    color: black;
                }}
            </style>
        </head>
        <body>
            <h1>Internship Listings for 2025</h1>
            <p>Generated on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            {str(table_tag)}
        </body>
        </html>
        """

        output_file = os.path.join("WebCrawler", "table_2025.html")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(styled_html)
        print(f" 2025 Internship table saved successfully: {output_file}")
        webbrowser.open(f"file://{os.path.abspath(output_file)}")

    else:
        print("⚠️ Table not found on the GitHub page. Check if the page structure changed.")

finally:
    driver.quit()
