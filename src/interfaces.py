# src/interfaces.py

from abc import ABC, abstractmethod

# Contract for storage
class IStorage(ABC):
    @abstractmethod
    def upload_file(self, local_path: str, remote_key: str, bucket_type: str) -> bool:
        """
        'analysis' for BOM or 'audit' for POM
        """
        pass


# Contract for version control
class IVersionControl(ABC):
    @abstractmethod
    def clone(self, url: str, target_path: str) -> bool:
        """
        Clone a repository for the destination path.
        """
        pass