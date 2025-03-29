import requests
from bs4 import BeautifulSoup
import subprocess
import sys
import os
import warnings
from urllib3.exceptions import NotOpenSSLWarning

# Suppress the warning in this script as well
warnings.filterwarnings("ignore", category=NotOpenSSLWarning)

def fetch_article(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        article_tag = soup.find("article")
        if article_tag:
            return article_tag.get_text(separator="\n", strip=True)
        else:
            return soup.get_text(separator="\n", strip=True)
    else:
        print("Failed to retrieve the webpage.", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 articleParser.py <URL>")
        sys.exit(1)
    
    url = sys.argv[1]
    article_text = fetch_article(url)
    
    if article_text:
        # Create a copy of the current environment and add the PYTHONWARNINGS variable
        env = os.environ.copy()
        env["PYTHONWARNINGS"] = "ignore"
        
        # Call geminiAPI.py as a subprocess with the updated environment
        result = subprocess.run(
            ["python3", "geminiAPI.py"],
            input=article_text,
            text=True,
            capture_output=True,
            env=env
        )
        
        if result.returncode != 0:
            print("Error in geminiAPI.py:", result.stderr)
        else:
            print("Generated Synopsis:")
            print(result.stdout)
