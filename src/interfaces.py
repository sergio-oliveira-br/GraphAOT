# src/interfaces.py

from abc import ABC, abstractmethod
import networkx as nx

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


# Contract for the extraction of artifacts
class IBuildTool(ABC):
    @abstractmethod
    def generate_bom(self, project_path: str) -> str:
        """Generates the CycloneDX SBOM"""
        pass

    @abstractmethod
    def generate_audit_data(self, project_path: str) -> str:
        """Generates the POM"""
        pass

# Contract for the architecture of Graphs
class GraphProvider(ABC):
    @abstractmethod
    def build_from_bom(self, bom_path: str) -> nx.DiGraph:
        """Transforms a BOM into a graph"""
        pass

    @abstractmethod
    def get_metrics(self, graph: nx.DiGraph) -> dict:
        """Extract topological metrics graph - (SRQ1)"""
        pass