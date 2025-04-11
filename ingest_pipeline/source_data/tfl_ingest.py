import os
import requests
from prefect import flow, task
from google.cloud import storage

# GCP setup
BUCKET_NAME = "de-project-449017-cms-bucket"
DESTINATION_FOLDER = "TFL"
CREDENTIALS_FILE = "tf_keys.json" 
client = storage.Client.from_service_account_json(CREDENTIALS_FILE)
bucket = client.bucket(BUCKET_NAME)

BASE_URL = "https://cycling.data.tfl.gov.uk/ActiveTravelCountsProgramme"

# Define all file patterns and years
patterns = {
    "Q1": {
        "pattern": "%d Q1 (Jan-Mar)-Central.csv",
        "years": range(2014, 2025)
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
        "years": range(2014, 2025)
    },
    "Q4": {
        "patterns": [
            "%d Q4 autumn (Oct-Dec)-Central.csv",
            "%d Q4 autumn (Oct-Dec)-Cycleways.csv"
        ],
        "years": range(2014, 2025)
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

# Prefect task: checks if file already exists in GCP bucket
@task
def file_exists(file_name):
    return bucket.blob(f"{DESTINATION_FOLDER}/{file_name}").exists(client)

# Prefect task: download CSV file from TFL and upload it to GCP
@task
def download_and_upload(file_name):
    url_safe_name = file_name.replace(" ", "%20")
    file_url = f"{BASE_URL}/{url_safe_name}"
    print(f"Fetching: {file_url}")

    response = requests.get(file_url)
    if response.status_code == 200:
        blob = bucket.blob(f"{DESTINATION_FOLDER}/{file_name}")
        blob.upload_from_string(response.content, content_type='text/csv')
        print(f"✅ Uploaded: {file_name}")
    else:
        print(f"❌ Failed to fetch: {file_url} (Status {response.status_code})")

# Prefect flow: orchestrates the ETL logic by combining all the above tasks
@flow(name="tfl-monthly-cycling-update")
def tfl_etl_flow():
    for key, data in patterns.items():
        if "pattern" in data:
            for year in data["years"]:
                file_name = data["pattern"] % year
                if not file_exists(file_name):
                    download_and_upload(file_name)
        elif "patterns" in data:
            for pattern in data["patterns"]:
                for year in data["years"]:
                    file_name = pattern % year
                    if not file_exists(file_name):
                        download_and_upload(file_name)
        elif "files" in data:
            for file_name in data["files"]:
                if not file_exists(file_name):
                    download_and_upload(file_name)

# This allows running the flow manually if needed
if __name__ == "__main__":
    tfl_etl_flow()
