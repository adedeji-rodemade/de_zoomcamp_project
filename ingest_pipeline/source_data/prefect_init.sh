#!/bin/bash
set -e

echo "🔁 Waiting for Prefect server to start..."
sleep 30

echo "✅ Building the TFL flow deployment..."
prefect deployment build tfl_ingest.py:tfl_etl_flow \
  --name "monthly-tfl-update" \
  --cron "0 23 28-31 * *" \
  --pool "default-agent-pool" \
  --output tfl-deployment.yaml

echo "📦 Applying the deployment..."
prefect deployment apply tfl-deployment.yaml

echo "🚀 Starting Prefect agent..."
prefect agent start --work-queue default
