-- Create external table to load all csv files from 2014 to 2024 into a table
CREATE OR REPLACE EXTERNAL TABLE `de-project-449017.dwh_cms_dataset.ext_tfl_data`
OPTIONS (
  format = 'CSV',
  uris = ['gs://de-project-449017-cms-bucket/TFL/*.csv'],
  skip_leading_rows = 1,
  field_delimiter = ',',
  ignore_unknown_values = true,
  allow_jagged_rows = true
)
;

-- Create and partitioned and clustered native table for efficient read operation
CREATE OR REPLACE TABLE `de-project-449017.dwh_cms_dataset.tfl_data`
PARTITION BY DATE
CLUSTER BY SiteID AS (
  SELECT * FROM `de-project-449017.dwh_cms_dataset.ext_tfl_data`
);