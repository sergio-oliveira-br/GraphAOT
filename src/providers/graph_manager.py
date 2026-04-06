# src/providers/graph_manager.py

import json
import networkx as nx
import logging
from src.interfaces.graph import GraphProvider

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
            G.add_node(root_id, type='root', name=root.get('name'), group=root.get('group', ''))

            # Add the components
            for comp in data.get('components', []):
                G.add_node(comp.get('bom-ref'),
                           type='dependency',
                           group=comp.get('group', ''),
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

        # Identify the root node (usually is the zero)
        roots = [n for n, d in graph.in_degree() if d == 0]
        root = roots[0] if roots else None

        max_depth = 0
        if root:
            path_lengths = nx.single_source_shortest_path_length(graph, root)
            max_depth = max(path_lengths.values()) if path_lengths else 0

        centrality = nx.betweenness_centrality(graph)

        top_hubs = sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:3]
        hub_names = [graph.nodes[node].get('name', node) for node, score in top_hubs if score > 0]

        return {
            "node_count": graph.number_of_nodes(),
            "edge_count": graph.number_of_edges(),
            "density": nx.density(graph),
            "max_depth": max_depth,
            "avg_coefficient": nx.average_clustering(graph.to_undirected()),
            "top_hubs": hub_names,
            # If it’s not a DAG (Directed Acyclic Graph), there are circular dependencies,
            # which is a nightmare for static compilation
            "is_dag": nx.is_directed_acyclic_graph(graph)
        }