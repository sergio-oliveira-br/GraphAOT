# src/providers/graph_manager.py

import json
import networkx as nx
import logging
from src.interfaces.graph import GraphProvider
from src.utils.logger import setup_logger


class NetworkXGraphManager(GraphProvider):
    def __init__(self):
        self.logger = setup_logger('networkX_graph_manager')

    def build_from_bom(self, bom_path: str) -> nx.DiGraph:
        logging.info(f"Building graph from {bom_path}")
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

            logging.info(f" [OK] Graph built from {bom_path}")
            return G
        except Exception as e:
            self.logger.error(f" [!] Error in build the graph: {e}")
            return nx.DiGraph()

    def get_metrics(self, graph: nx.DiGraph) -> dict:
        return {
            **GraphMetrics.basic(graph),
            **GraphMetrics.hubs(graph),
            **GraphMetrics.centrality(graph),
            **GraphMetrics.clustering(graph),
            **GraphMetrics.transitivity(graph)
        }

class GraphMetrics:

    @staticmethod
    def basic(graph: nx.DiGraph) -> dict:
        node_count = graph.number_of_nodes()
        metrics = {
            'node_count': node_count,
            'edge_count': graph.number_of_edges(),
            'density': nx.density(graph) if node_count > 0 else 0.0,
            'is_dag': nx.is_directed_acyclic_graph(graph) if node_count > 0 else True
        }
        metrics['max_depth'] = GraphMetrics._compute_max_depth(graph) if metrics['is_dag'] and node_count > 0 else None
        return metrics

    @staticmethod
    def _compute_max_depth(graph: nx.DiGraph) -> int:
        try:
            if nx.is_directed_acyclic_graph(graph):
                return nx.dag_longest_path_length(graph)

            und = graph.to_undirected()
            longest = 0
            for n in und.nodes():
                lengths = nx.single_source_shortest_path_length(und, n)
                if lengths:
                    longest = max(longest, max(lengths.values()))
            return longest

        except Exception:
            return 0

    @staticmethod
    def hubs(graph: nx.DiGraph, top_n: int = 5) -> dict:
        if graph.number_of_nodes() == 0:
            return {'hubs': []}

        degree_dict = dict(graph.degree())
        hubs_sorted = sorted(degree_dict.items(), key=lambda x: x[1], reverse=True)
        return {'hubs': [n for n, _ in hubs_sorted[:top_n]]}

    @staticmethod
    def centrality(graph: nx.DiGraph) -> dict:
        n = graph.number_of_nodes()
        if n == 0:
            return {
                'degree_centrality_avg': 0.0,
                'betweenness_centrality_avg': 0.0,
                'closeness_centrality_avg': 0.0
            }
        deg = nx.degree_centrality(graph)
        bet = nx.betweenness_centrality(graph)
        clo = nx.closeness_centrality(graph)

        return {
            'degree_centrality_avg': sum(deg.values()) / n,
            'betweenness_centrality_avg': sum(bet.values()) / n,
            'closeness_centrality_avg': sum(clo.values()) / n
        }

    @staticmethod
    def clustering(graph: nx.DiGraph) -> dict:
        n = graph.number_of_nodes()
        if n == 0 or nx.is_directed_acyclic_graph(graph):
            return {'clustering_coeff_avg': 0.0}

        clustering_vals = nx.clustering(graph.to_undirected())
        return {'clustering_coeff_avg': sum(clustering_vals.values()) / n}

    @staticmethod
    def transitivity(graph: nx.DiGraph) -> dict:
        n = graph.number_of_nodes()
        if n == 0:
            return {'transitive_ratio': 0.0}

        direct_deps = sum(1 for _, d in graph.in_degree() if d == 0)
        return {'transitive_ratio': (n - direct_deps) / n}