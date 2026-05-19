# src/interfaces/stats.py

from abc import ABC, abstractmethod

# Statistics manager
class StatsProvider(ABC):
    @abstractmethod
    def save_metrics(self, project_id: str, metrics: dict):
        pass

    @abstractmethod
    def _initialize_storage(self):
        """create file or table"""
        pass

    @abstractmethod
    def compute_migration_metrics(self, graph_metrics: dict, aot_results: dict) -> dict:
        """Compute metrics needed for migration"""
        pass
