# src/interfaces.py

from abc import ABC, abstractmethod

class IStorage(ABC):
    @abstractmethod
    def upload_file(self, local_path: str, remote_key: str, bucket_type: str) -> bool:
        pass

class IVersionControl(ABC):
    @abstractmethod
    def clone(self, url: str, target_path: str) -> bool:
        """
        Clone a repository for the destination path.
        """
        pass