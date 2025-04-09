import os
import requests
from google.cloud import storage


# GCP Bucket details
BUCKET_NAME = "de-project-449017-cms-bucket"
DESTINATION_FOLDER = "TFL"
CREDENTIALS_FILE = "/workspaces/de_zoomcamp_project/ingest_pipeline/terraform_setup/Keys/tf_keys.json"

# Initialize GCP storage client with service account
client = storage.Client.from_service_account_json(CREDENTIALS_FILE)
bucket = client.bucket(BUCKET_NAME)

# Base URL for dataset
BASE_URL = "https://cycling.data.tfl.gov.uk/ActiveTravelCountsProgramme"

# File patterns and year ranges
patterns = {
    "Q1": {
        "pattern": "%d Q1 (Jan-Mar)-Central.csv",
        "years": range(2014, 2023)
    },
    "Q2": {
        "patterns": [
            "%d Q2 spring (Apr-Jun)-Central.csv",
            "%d Q2 spring (Apr-Jun)-Cycleways.csv",
            "%d Q2 spring (Apr-Jun)-Inner.csv",
            "%d Q2 spring (Apr-Jun)-Outer.csv",
            "%d Q2 spring (synthetic)-Central.csv",
            "%d Q2 spring (synthetic)-Inner.csv",
            "%d Q2 spring (synthetic)-Outer.csv",
        ],
        "years": range(2015, 2021)
    },
    "Q3": {
        "pattern": "%d Q3 (Jul-Sep)-Central.csv",
        "years": range(2014, 2023)
    },
    "Q4": {
        "patterns": [
            "%d Q4 autumn (Oct-Dec)-Central.csv",
            "%d Q4 autumn (Oct-Dec)-Cycleways.csv"
        ],
        "years": range(2014, 2023)
    },
    "W1": {
        "patterns": [
            "%d W1 spring-Central.csv",
            "%d W1 spring-Cycleways.csv",
            "%d W1 spring-Inner-Part1.csv",
            "%d W1 spring-Inner-Part2.csv",
            "%d W1 spring-Outer.csv"
        ],
        "years": range(2022, 2025)
    },
    "W2": {
        "pattern": "%d W2 autumn-Cycleways.csv",
        "years": range(2022, 2025)
    }
}

# Function to download and upload to GCP
def download_and_upload(file_name):
    url_safe_name = file_name.replace(" ", "%20")
    file_url = f"{BASE_URL}/{url_safe_name}"
    print(f"Fetching: {file_url}")

    response = requests.get(file_url)
    if response.status_code == 200:
        blob = bucket.blob(f"{DESTINATION_FOLDER}/{file_name}")
        blob.upload_from_string(response.content, content_type='text/csv')
        print(f"Uploaded: {file_name}")
    else:
        print(f"Failed to fetch: {file_url} (Status {response.status_code})")

# Loop through all patterns and process files
for key, data in patterns.items():
    if "pattern" in data:
        for year in data["years"]:
            file_name = data["pattern"] % year
            download_and_upload(file_name)
    elif "patterns" in data:
        for pattern in data["patterns"]:
            for year in data["years"]:
                file_name = pattern % year
                download_and_upload(file_name)
    elif "files" in data:
        for file_name in data["files"]:
            download_and_upload(file_name)