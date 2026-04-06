# src/interfaces/metadata.py

from abc import ABC, abstractmethod

# extraction of the metadata volume
class MetadataProvider(ABC):
    @abstractmethod
    def get_metadata_volume(self, group: str, artifact: str, version: str) -> dict:
        """Returns the count of configuration inputs (Reflection, JNI, Proxy)."""
        pass