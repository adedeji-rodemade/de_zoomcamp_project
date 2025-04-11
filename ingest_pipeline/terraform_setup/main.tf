terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "6.17.0"
    }
  }
}

provider "google" {
  # Credentials only needs to be set if you do not have the GOOGLE_APPLICATION_CREDENTIALS set
  credentials = "./Keys/tf_keys.json"
  project = "de-project-449017"
  region  = "europe-west3"
}



resource "google_storage_bucket" "de-data-bucket" {
  name     = "de-project-449017-cms-bucket"
  location = "US"

  # Optional, but recommended settings:
  storage_class               = "STANDARD"
  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }

  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age = 30 // days
    }
  }

  force_destroy = true
}


resource "google_bigquery_dataset" "cms_dataset" {
  dataset_id = "dwh_cms_dataset"
  project    = "de-project-449017"
  location   = "US"
}