import os
import requests
import zipfile
import io
from google.cloud import storage
import pandas as pd
from tqdm import tqdm

# GCP Bucket details
BUCKET_NAME = "de-project-449017-cms-bucket"
DESTINATION_FOLDER = "general_payment_data"

#If you authenticated through the GCP SDK you can comment out these two lines
CREDENTIALS_FILE = "/workspaces/de_zoomcamp_project/ingest_pipeline/terraform_setup/Keys/tf_keys.json"  
client = storage.Client.from_service_account_json(CREDENTIALS_FILE)


# Base URL pattern for Open Payments dataset
BASE_URL = "https://download.cms.gov/openpayments/PGYR{year}_P01302025_01212025.zip"

# Years to fetch
years = range(2019, 2024)  # 2019 to 2023

# Initialize GCP Storage Client
# storage_client = storage.Client()

def upload_to_gcs(bucket_name, destination_blob_name, file_obj):
    """Uploads file to GCP bucket as a binary stream."""
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    
    # Convert string to bytes to avoid TypeError
    file_obj.seek(0)  # Ensure the cursor is at the start
    binary_stream = io.BytesIO(file_obj.getvalue().encode("utf-8"))

    blob.upload_from_file(binary_stream, rewind=True)
    print(f"Uploaded {destination_blob_name} to {bucket_name}")

def process_and_upload_csv(year):
    """Downloads ZIP, extracts relevant CSV, and uploads to GCP."""
    url = BASE_URL.format(year=year)
    print(f"Processing {year} data from {url}...")

    # Step 1: Download ZIP file
    response = requests.get(url, stream=True)
    if response.status_code != 200:
        print(f"Failed to download {url}")
        return
    
    zip_file = zipfile.ZipFile(io.BytesIO(response.content))

    # Step 2: Extract the required CSV
    for file_name in zip_file.namelist():
        if "OP_DTL_GNRL" in file_name and file_name.endswith(".csv"):
            print(f"Extracting {file_name} from {year} dataset...")
            
            with zip_file.open(file_name) as csv_file:
                # Read in chunks to handle large file sizes efficiently
                chunk_iter = pd.read_csv(csv_file, chunksize=500000, low_memory=False)

                # Upload each chunk separately
                for i, chunk in tqdm(enumerate(chunk_iter), desc=f"Uploading {year}"):
                    destination_path = f"{DESTINATION_FOLDER}{year}/{file_name.replace('.csv', '')}_part{i}.csv"
                    chunk_csv = io.StringIO()
                    chunk.to_csv(chunk_csv, index=False)
                    chunk_csv.seek(0)

                    # Upload chunk to GCP
                    upload_to_gcs(BUCKET_NAME, destination_path, chunk_csv)

# Process all years dynamically
for year in years:
    process_and_upload_csv(year)

print("Data processing and upload complete.")
