"""
    This is for new executive orders. Just to see what we have not gotten yet in the DB
"""
import pandas as pd
import io
import requests
import fitz
import time

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

def get_recent_ten_orders():
    # API endpoint for the Federal Register documents
    url = "https://www.federalregister.gov/api/v1/documents.json"

    params = {
    'conditions[correction]': 0,
    'conditions[presidential_document_type]': 'executive_order',
    'conditions[type][]': 'PRESDOCU',
    'fields[]': ['citation', 'document_number', 'end_page', 'html_url', 'pdf_url', 'type', 'subtype', 'publication_date', 'signing_date', 'start_page', 'title', 'disposition_notes', 'executive_order_number', 'not_received_for_publication', 'full_text_xml_url', 'body_html_url', 'json_url'],
    'include_pre_1994_docs': 'true',
    'maximum_per_page': 10000,
    'order': 'executive_order',
    'per_page': 10000
    }

    # Send GET request to the API
    response = requests.get(url, params=params)

    # Check if the request was successful (HTTP status code 200)
    if response.status_code == 200:
        new_orders = pd.DataFrame(response.json()['results'])
        new_orders['order_text'] = new_orders['pdf_url'].apply(extract_pdf_text_from_url)
        return new_orders
        
    else:
        print(f"Failed to retrieve data. HTTP Status code: {response.status_code}")
    
