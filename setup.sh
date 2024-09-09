#!/bin/bash

# Set your project ID and region
PROJECT_ID="YOUR_PROJECT_ID"  # Replace with your actual project ID
REGION="YOUR_REGION"          # Replace with your preferred region (e.g., us-central1)

# Bucket name (make this globally unique)
BUCKET_NAME="gemini-demos-assets-${PROJECT_ID}"

# Enable required APIs (add Cloud Storage API)
gcloud services enable \
  aiplatform.googleapis.com \
  cloudbuild.googleapis.com \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  iam.googleapis.com \
  storage-api.googleapis.com \
  --project="${PROJECT_ID}"

# Create Cloud Storage bucket
gsutil mb -l "${REGION}" gs://"${BUCKET_NAME}"

# Create Artifact Registry repository if needed 
gcloud artifacts repositories create "dev-lifecycle" \
  --repository-format=docker \
  --location="${REGION}" \
  --description="Docker repository for Gemini Development Lifecycle demos" \
  --project="${PROJECT_ID}"

# Deploy to Cloud Run, passing the bucket name as an environment variable
gcloud run deploy dev-lifecycle \
  --source="./" \
  --region="${REGION}" \
  --allow-unauthenticated \
  --set-env-vars "DEMO_ASSETS_BUCKET=gs://${BUCKET_NAME}" \
  --project="${PROJECT_ID}"

echo "Deployment process started. Check Cloud Run console for progress." 