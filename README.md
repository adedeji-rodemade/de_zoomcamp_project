# 🚴️ TfL Cycling Data Pipeline Project

## 📀 Overview

This project is the final capstone project of the DataTalksClub DE Zoomcamp. It's a complete end-to-end data engineering pipeline built to ingest, transform, and visualize cycling data from the [Transport for London (TfL) Active Travel Counts Programme](https://cycling.data.tfl.gov.uk/). The pipeline automates the collection of quarterly and seasonal cycling count data available as CSV files on the TfL open data portal and enables efficient analysis of long-term trends in cycling activity across London.

## 📊 Problem Statement

As cycling becomes an increasingly critical mode of transport in London, Transport for London (TfL) collects quarterly data to monitor cycling activity across various boroughs and strategic routes. This data helps inform infrastructure planning, track the impact of active travel policies, and promote sustainable transport initiatives.

However, this rich dataset is published as dozens of individual CSV files on TfL’s website, organized by year and season, with manual updates and no API access. This structure makes it difficult for analysts and planners to consolidate, maintain, and analyze the data efficiently.

This project addresses the need for a scalable and automated pipeline that:
- Consolidates and stores all TfL cycling programme files across years and seasons into a unified dataset
- Enables monthly scheduled ingestion of new data files as they are published
- Cleans and transforms the data for easy querying and reporting
- Powers an interactive dashboard to uncover trends in cycling growth, seasonal fluctuations, regional hotspots, and infrastructure usage across London

The final product supports stakeholders in:
- Monitoring the effectiveness of cycling policies
- Identifying underserved regions for new cycling infrastructure
- Understanding seasonal and regional trends in cycling behavior

## 📅 Project Pipeline Summary

### 1. 📂 Data Ingestion (via Batch Processing)
**Goal**: Automatically download new CSV files from TfL and store them in a GCP bucket.

- ✅ **Terraform** is used to provision:
  - Google Cloud Storage (GCS) bucket
  - BigQuery dataset

- ✅ **Python + Prefect** orchestrates the ingestion:
  - File URL patterns are used to programmatically identify available files from 2014 to present
  - A monthly scheduled Prefect flow checks for new files and uploads them to the GCS bucket
  - Duplicate files are avoided by checking the bucket before download

- ✅ The orchestration runs in **Docker** containers, with configuration found in `docker-compose.yml`

> 📄 All code for this stage is in the [`ingest_pipeline`](./ingest_pipeline) folder

### 2. 📊 Loading to BigQuery
**Goal**: Load all uploaded CSVs in the bucket into a unified BigQuery external table.

- A single **external table** is created in BigQuery referencing all files in the bucket
- The load script auto-infers schema and allows centralized querying across historical records

> 📄 See [`loading_pipeline`](./loading_pipeline) folder

### 3. 📈 Data Transformation with dbt Cloud
**Goal**: Transform raw data into analytics-ready tables for reporting

- **Staging models** clean and cast columns from the external source table
- **Fact models** summarize cycling counts and segment them by different dimensions for quick dashboard exploration.

> 📄 dbt models are built and versioned in **dbt Cloud** for CI/CD and documentation

### 4. 📅 Dashboard Development
**Goal**: Provide actionable insights on cycling behavior trends in London

- Built with **Google Looker Studio**
- Powered directly from final dbt models in BigQuery
- Allows slicing by:
  - Region (Central, Inner, Outer, Cycleways)
  - Year, Quarter, and Season
  - Borough-specific observations

> 📄 See [`tfl-dashboard`](./tfl-dashboard) jpg for overview of the insights.

---

## 🔧 Tools and Technologies

| Tool/Platform | Purpose |
| ------------- | ------- |
| Python        | Scripting the ingest pipeline |
| Prefect       | Flow orchestration and scheduling |
| Docker        | Containerizing pipeline scripts |
| Terraform     | Infrastructure provisioning on GCP |
| GCP           | Cloud storage and data warehouse (BigQuery) |
| dbt Cloud     | Data transformation and modeling |
| Looker Studio | Dashboarding and data visualization |

---

## 🚀 Getting Started

### Prerequisites
- GCP project + service account key 
- Installations: Docker, Prefect, Terraform

### Setup
```bash
git clone https://github.com/adedeji-rodemade/de_zoomcamp_project.git
cd de_zoomcamp_project/ingest_pipeline/source_data
```

### Deploy Infrastructure
```bash
cd ../terraform_setup
terraform init
terraform apply
```

### Run the Flow Locally via Docker Compose
```bash
docker-compose up --build
```

Access Prefect UI via forwarded port:
```
http://127.0.0.1:4200
```
Trigger the `tfl-monthly-cycling-update` flow manually or let it run at month-end automatically.

---

## 📊 Outcome

This pipeline successfully consolidates over 10 years of quarterly cycling data into a centralized BigQuery table, enabling:
- Rapid time series analysis of cycling trends
- Seasonality breakdown and growth patterns
- Granular filtering by London regions

The dashboard serves as a public-facing, stakeholder-friendly tool for cycling infrastructure evaluation.

---

## 🛍️ Resources

- [TfL Active Travel Programme Documentation](https://cycling.data.tfl.gov.uk/ActiveTravelCountsProgramme/0%20Strategic%20active%20travel%20counts%20-%20release%20note.pdf)
- [Dataset Link](https://cycling.data.tfl.gov.uk/)

---

## 📢 Contact
For inquiries or feedback, feel free to reach out via [GitHub Issues](https://github.com/adedeji-rodemade/de_zoomcamp_project/issues).

---

🏆 **Submitted as part of the DataTalksClub Data Engineering Zoomcamp Capstone Project.**

