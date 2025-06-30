import os
from google.cloud import storage
from google.cloud.exceptions import NotFound
import tempfile

class CloudStorageManager:
    def __init__(self, bucket_name=None):
        """Initialize Google Cloud Storage manager."""
        self.client = storage.Client()
        self.bucket_name = bucket_name or os.getenv('GCS_BUCKET_NAME')
        if not self.bucket_name:
            raise ValueError("GCS_BUCKET_NAME environment variable must be set")
        
        self.bucket = self.client.bucket(self.bucket_name)
    
    def upload_file(self, local_file_path, cloud_file_name):
        """Upload a file to Google Cloud Storage."""
        blob = self.bucket.blob(cloud_file_name)
        blob.upload_from_filename(local_file_path)
        print(f"Uploaded {local_file_path} to gs://{self.bucket_name}/{cloud_file_name}")
        return f"gs://{self.bucket_name}/{cloud_file_name}"
    
    def download_file(self, cloud_file_name, local_file_path):
        """Download a file from Google Cloud Storage."""
        blob = self.bucket.blob(cloud_file_name)
        blob.download_to_filename(local_file_path)
        print(f"Downloaded gs://{self.bucket_name}/{cloud_file_name} to {local_file_path}")
    
    def file_exists(self, cloud_file_name):
        """Check if a file exists in Google Cloud Storage."""
        blob = self.bucket.blob(cloud_file_name)
        return blob.exists()
    
    def list_files(self, prefix=""):
        """List files in the bucket with optional prefix."""
        blobs = self.client.list_blobs(self.bucket_name, prefix=prefix)
        return [blob.name for blob in blobs]
    
    def delete_file(self, cloud_file_name):
        """Delete a file from Google Cloud Storage."""
        blob = self.bucket.blob(cloud_file_name)
        blob.delete()
        print(f"Deleted gs://{self.bucket_name}/{cloud_file_name}")
    
    def get_temp_file(self, cloud_file_name):
        """Download a file to a temporary location and return the path."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(cloud_file_name)[1]) as tmp_file:
            self.download_file(cloud_file_name, tmp_file.name)
            return tmp_file.name 