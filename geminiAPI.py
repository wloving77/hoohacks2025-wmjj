import sys
from google import genai
import warnings
from urllib3.exceptions import NotOpenSSLWarning

# Suppress the NotOpenSSLWarning
warnings.filterwarnings("ignore", category=NotOpenSSLWarning)

def generate_synopsis(text):
    # Replace with your actual API key
    client = genai.Client(api_key="")
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents="Give a synopsis of: " + text
    )
    return response.text

if __name__ == "__main__":
    # Read the entire input from standard input
    input_text = sys.stdin.read()
    if not input_text:
        print("No input text provided.", file=sys.stderr)
        sys.exit(1)
    synopsis = generate_synopsis(input_text)
    print(synopsis)
