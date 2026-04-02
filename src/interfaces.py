# src/interfaces.py

from abc import ABC, abstractmethod

class IStorage(ABC):
    @abstractmethod
    def upload_file(self, local_path: str, remote_key: str, bucket_type: str) -> bool:
        pass