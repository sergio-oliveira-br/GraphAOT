# src/providers/graph_manager.py

import json
import networkx as nx
import logging
from src.interfaces import GraphProvider

class NetworkXGraphManager(GraphProvider):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def build_from_bom(self, bom_path: str) -> nx.DiGraph:
        try:
            with open(bom_path, 'r') as f:
                data = json.load(f)

            G = nx.DiGraph()

            # Add the root project
            root = data.get('metadata', {}).get('component', {})
            root_id = root.get('bom-ref', 'root')
            G.add_node(root_id, type='root', name=root.get('name'))

            # Add the components
            for comp in data.get('components', []):
                G.add_node(comp.get('bom-ref'),
                           name=comp.get('name'),
                           version=comp.get('version'))

            # build the edges (Dependencies)
            for dep in data.get('dependencies', []):
                source = dep.get('ref')
                for target in dep.get('dependsOn', []):
                    if G.has_node(source) and G.has_node(target):
                        G.add_edge(source, target)

            return G
        except Exception as e:
            self.logger.error(f"Error in build the graph: {e}")
            return nx.DiGraph()

    def get_metrics(self, graph: nx.DiGraph) -> dict:
        if graph.number_of_nodes() == 0:
            return {}

        return {
            "node_count": graph.number_of_nodes(),
            "edge_count": graph.number_of_edges(),
            "avg_clustering": nx.average_clustering(graph.to_undirected()),
            "density": nx.density(graph)
        }