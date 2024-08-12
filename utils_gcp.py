from google.cloud import secretmanager
import os 

PROJECT_ID = os.environ.get("GCP_PROJECT")  # Your Google Cloud Project ID
PROJECT_NUMBER = os.environ.get("GCP_NUMBER")  # Your Google Cloud Project NUmber


def access_secret_version(secret_id, version_id="latest"):
    # Create the Secret Manager client.
    client = secretmanager.SecretManagerServiceClient()

    # Build the resource name of the secret version.
    name = f"projects/{GCP_NUMBER}/secrets/{secret_id}/versions/1"

    # Access the secret version.
    response = client.access_secret_version(name=name)

    # Return the decoded payload.
    return response.payload.data.decode('UTF-8')
