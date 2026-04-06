# src/interfaces/vcs.py

from abc import ABC, abstractmethod

# Contract for version control
class VersionControl(ABC):
    @abstractmethod
    def clone(self, url: str, target_path: str) -> bool:
        """ Clone a repository for the destination path"""
        pass