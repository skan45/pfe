from .minioProvider import get_minio_client, create_bucket_if_not_exists
from botocore.exceptions import NoCredentialsError
import os

# Bucket name for storing invoices
BUCKET_NAME = 'factures'  # You can change the name if needed

def upload_file_to_minio(file, bucket_name=BUCKET_NAME, client_id=None):
    """Upload a file to MinIO bucket and return the URL of the uploaded file."""
    # Create the bucket if it doesn't exist
    create_bucket_if_not_exists(bucket_name)
    
    # Get MinIO client
    s3_client = get_minio_client()

    # Define a unique file name for each upload (you can customize this)
    file_name = f'{client_id}/{file.name}' if client_id else file.name

    try:
        # Upload file to the MinIO bucket
        s3_client.upload_fileobj(
            file, bucket_name, file_name,
            ExtraArgs={'ContentType': file.content_type}  # You can set the MIME type if needed
        )
        print(f"File {file_name} uploaded successfully to bucket {bucket_name}")

        # Construct the URL to access the file
        file_url = f'http://localhost:9000/{bucket_name}/{file_name}'  
        return file_url
    except NoCredentialsError:
        print("No valid credentials found for MinIO")
    except Exception as e:
        print(f"Failed to upload file {file_name}: {str(e)}")
        return None
