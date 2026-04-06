# src/providers/s3_storage.py

import boto3
import logging
from src.interfaces.storage import FileStorage

class S3Storage(FileStorage):
    def __init__(self, bucket_name: str):
        self.bucket_name = bucket_name
        self.s3_client = boto3.client('s3')
        self.logger = logging.getLogger(__name__)

    def upload_file(self, local_path: str, remote_key: str, bucket_type: str) -> bool:
        # There are two folders in the S3, one for POM and the other for BOM
        prefix = "analysis" if bucket_type == "analysis" else "audit-logs"
        full_key = f"{prefix}/{remote_key}"

        try:
            self.s3_client.upload_file(local_path, self.bucket_name, full_key)
            self.logger.info(f"Success: {local_path} -> s3://{self.bucket_name}/{full_key}")
            return True

        except Exception as e:
            self.logger.error(f"Error uploading {local_path}: {str(e)}")
            return False

    def download_file(self, s3_key, local_path):
        try:
            self.s3_client.download_file(self.bucket_name, s3_key, local_path)
            return True

        except Exception as e:
            print(f"Error on downloading from S3: {e}")
            return False