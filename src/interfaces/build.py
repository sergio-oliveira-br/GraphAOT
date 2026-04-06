# src/interfaces/build.py

from abc import ABC, abstractmethod

# Contract for the extraction of artifacts
class BuildTool(ABC):
    @abstractmethod
    def generate_bom(self, project_path: str) -> str:
        """Generates the CycloneDX SBOM"""
        pass

    @abstractmethod
    def generate_audit_data(self, project_path: str) -> str:
        """Generates the POM"""
        pass