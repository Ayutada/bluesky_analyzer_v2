import os
import requests
import re
import time  # New: Used to rest the crawler to prevent being banned
from bs4 import BeautifulSoup
from markdownify import markdownify as md

# --- Configuration Area ---
OUTPUT_FOLDER = "rag_docs\jp"

# Define the code list of 16 personality types
MBTI_TYPES = [
    "INTJ", "INTP", "ENTJ", "ENTP",
    "INFJ", "INFP", "ENFJ", "ENFP",
    "ISTJ", "ISFJ", "ESTJ", "ESFJ",
    "ISTP", "ISFP", "ESTP", "ESFP"
]

def fetch_and_save(url, folder):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    print(f"Fetching: {url} ...")
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        response.encoding = 'utf-8'

        soup = BeautifulSoup(response.text, "html.parser")
        
        # Process file name (remove illegal characters)
        if soup.title and soup.title.string:
            raw_title = soup.title.string.strip()
            page_title = re.sub(r'[\\/*?:"<>|]', "_", raw_title)
        else:
            page_title = "Unknown_Title_" + str(int(time.time()))
        
        # Extract content and convert to Markdown
        content_html = str(soup.body) 
        markdown_content = md(content_html, heading_style="ATX")

        # Check folder
        if not os.path.exists(folder):
            os.makedirs(folder)
            
        file_path = os.path.join(folder, f"{page_title}.md")
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"# Source: {url}\n\n")
            f.write(markdown_content)
            
        print(f"Successfully saved: {file_path}")

    except Exception as e:
        print(f"Failed to crawl this page: {url}")
        print(f"   Error message: {e}")

if __name__ == "__main__":
    print(f"Starting batch crawling for 16 personality types, total {len(MBTI_TYPES)} tasks...\n")
    
    for mbti_type in MBTI_TYPES:
        # Construct URL: usually /ch/code-personality, note that code is usually lowercase
        # Example: https://www.16personalities.com/ch/intj-personality
        target_url = f"https://www.16personalities.com/ja/{mbti_type.lower()}型の性格"
        
        fetch_and_save(target_url, OUTPUT_FOLDER)
        
        # The wait here is crucial, be a polite crawler
        print("Resting for 2 seconds, preparing for the next...") 
        time.sleep(2)
        
    print("\nAll tasks completed!")