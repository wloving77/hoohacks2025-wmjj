"""
    This is for new executive orders. Just to see what we have not gotten yet in the DB
"""
import requests

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
        data = response.json()
        return data['results']
       
        
    else:
        print(f"Failed to retrieve data. HTTP Status code: {response.status_code}")
    
