import os
import json
import requests

# Create the jsons folder if it doesn't exist
folder = "jsons"
os.makedirs(folder, exist_ok=True)

# Base URL and API key configuration
url = "https://api.congress.gov/v3/summaries"
api_key = "1IqjUQSesVf3nXAVxzazyTAXmux4KvcHuAjkCczc"

# Define other query parameters that remain constant
base_params = {
    "api_key": api_key,
    "format": "json",
    "fromDateTime": "2025-01-20T00:00:00Z",
    "toDateTime": "2025-03-29T00:00:00Z",
    "sort": "updateDate+asc"
}

limit = 1078  # maximum number of records per request
offset = 0   # starting record

while True:
    # Update parameters with current offset and limit
    params = base_params.copy()
    params.update({
        "offset": offset,
        "limit": limit
    })
    
    print(f"Requesting records {offset} to {offset + limit - 1}...")
    response = requests.get(url, params=params)
    
    if response.status_code != 200:
        print(f"Query failed with status code {response.status_code}: {response.text}")
        break

    data = response.json()
    
    # Save the JSON response to a file
    file_path = os.path.join(folder, f"legislativeSummaries.json")
    with open(file_path, "w") as json_file:
        json.dump(data, json_file, indent=4)
    print(f"Saved data for offset {offset} to {file_path}")

    # Check if the returned data is less than the limit, meaning we've reached the end.
    if len(data.get("results", [])) < limit:
        print("No more data to fetch.")
        break

    # Increment offset for the next batch
    offset += limit
