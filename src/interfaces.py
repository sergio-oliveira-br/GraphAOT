# src/interfaces.py

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