import requests
import time
import json
import os

API_KEY = "your_api_key_here"
BASE_URL = "https://api.goperigon.com/v1/stories/all"
OUTPUT_FILE = "perigon_us_politics_2025.json"

def safe_request(url, params, max_retries=5):
    for attempt in range(max_retries):
        response = requests.get(url, params=params)
        if response.status_code == 429:
            wait_time = 2 ** attempt
            print(f"Rate limited (429). Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
        elif response.status_code != 200:
            print(f"Error {response.status_code}: {response.text}")
            time.sleep(2)
        else:
            return response
    raise Exception("Too many failed attempts. Aborting.")

def fetch_all_stories():
    all_stories = []
    page = 1

    # Initial request to get total results
    base_params = {
        "category": "Politics",
        "from": "2025-01-01T00:00:00",
        "size": 100,
        "country": "us",
        "topic": "US Politics",
        "sortBy": "count",
        "showNumResults": "true",
        "apiKey": API_KEY,
    }

    print("Getting total number of results...")
    initial = safe_request(BASE_URL, {**base_params, "page": 1}).json()
    total_results = initial.get("numResults", 0)
    total_pages = (total_results + 99) // 100
    print(f"Total results: {total_results} (~{total_pages} pages)")

    # Start pagination
    while page <= total_pages:
        print(f"⬇️  Fetching page {page}/{total_pages}...")
        params = {**base_params, "page": page}
        response = safe_request(BASE_URL, params)

        data = response.json()
        stories = data.get("results", [])

        if not stories:
            print("No stories found on this page. Stopping early.")
            break

        all_stories.extend(stories)
        page += 1
        time.sleep(0.5)  # Prevent burst rate issues

    return all_stories

def save_to_json(data, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(data)} stories to {os.path.abspath(path)}")

if __name__ == "__main__":
    stories = fetch_all_stories()
    save_to_json(stories, OUTPUT_FILE)