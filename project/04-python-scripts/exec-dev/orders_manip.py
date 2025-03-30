import pandas as pd
import io
import requests
import fitz
import time
"""
    file for looking at and converting the executive orders CSV file
"""

orders = pd.read_csv("project/exec-dev/executive_orders.csv")

# Function to extract text from a PDF given a URL
def extract_pdf_text_from_url(url):
    try:
        # Get the PDF content from the URL
        response = requests.get(url)
        response.raise_for_status()  # Ensure the request was successful
        pdf = io.BytesIO(response.content)
        
        # Open the PDF and extract text
        with fitz.open(stream=pdf) as doc:
            text = ""
            for page in doc:
                text += page.get_text()
        return text
    except Exception as e:
        return f"Error processing URL {url}: {str(e)}"


# Apply the function to the DataFrame
print("Applying text extraction algorithm to the dataframe")
orders['order_text'] = orders['pdf_url'].apply(extract_pdf_text_from_url)
print("done with orders")

# Show the resulting DataFrame with extracted text

orders.to_csv("project/exec-dev/executive_orders.csv", index=False)

# choose model 
# model = SentenceTransformer('all-MiniLM-L6-v2')  

# create the embeddings
# orders['embedding'] = orders['pdf_text'].apply(lambda x: model.encode(x))

