import boto3
from botocore.exceptions import NoCredentialsError

# Configuration for MinIO 
MINIO_ENDPOINT = "minio:9000"  
MINIO_ACCESS_KEY = "minioadmin"  
MINIO_SECRET_KEY = "minioadmin" 
MINIO_USE_SSL = False  # Set to True if using HTTPS (SSL)

def get_minio_client():
    """Returns a MinIO client configured with the endpoint and credentials"""
    s3_client = boto3.client(
        's3',
        endpoint_url=f"http{'s' if MINIO_USE_SSL else ''}://{MINIO_ENDPOINT}",
        aws_access_key_id=MINIO_ACCESS_KEY,
        aws_secret_access_key=MINIO_SECRET_KEY,
        region_name='us-east-1',  # You can change the region 
    )
    return s3_client

def create_bucket_if_not_exists(bucket_name):
    """Create a bucket in MinIO if it doesn't exist"""
    s3_client = get_minio_client()
    try:
        s3_client.head_bucket(Bucket=bucket_name)  # Check if the bucket exists
    except NoCredentialsError:
        print("No valid credentials found for MinIO")
        return False
    except Exception as e:
        print(f"Bucket {bucket_name} does not exist. Creating it now.")
        s3_client.create_bucket(Bucket=bucket_name)
        print(f"Bucket {bucket_name} created successfully.")
        return True
