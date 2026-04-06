# src/interfaces.py

from abc import ABC, abstractmethod
import networkx as nx




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

# Statistics manager
class StatsProvider(ABC):
    @abstractmethod
    def save_metrics(self, project_id: str, metrics: dict):
        pass

    @abstractmethod
    def _initialize_storage(self):
        """create file or table"""
        pass