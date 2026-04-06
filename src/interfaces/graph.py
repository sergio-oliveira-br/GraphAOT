# src/interfaces/graph.py

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