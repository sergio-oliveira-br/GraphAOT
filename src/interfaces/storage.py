# src/interfaces/storage.py

from abc import ABC, abstractmethod

# Contract for storage
class IStorage(ABC):
    @abstractmethod
    def upload_file(self, local_path: str, remote_key: str, bucket_type: str) -> bool:
        """'analysis' for BOM or 'audit' for POM"""
        pass

    @abstractmethod
    def download_file(self, s3_key, local_path):
        """ Download file from s3 to local path"""
        pass