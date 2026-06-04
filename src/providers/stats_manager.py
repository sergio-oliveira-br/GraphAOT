# src/providers/stats_manager.py

import pandas as pd
import os

from pathlib import Path
from datetime import datetime

from src.dto.metrics_dto import MetricsDTO
from src.interfaces.stats import StatsProvider
from src.utils.logger import setup_logger


CSV_COLUMNS = [
    "project_id",
    # SRQ1
    "node_count", "edge_count", "density", "max_depth", "is_dag", "hubs",
    # SRQ2
    "dep_count", "reflection_count", "method_count", "serializable_count", "resources_count",
    "total_metadata", "metadata_density",
    "build_status", "processed_at"
]

class StatsManager(StatsProvider):
    def __init__(self, output_path: str = "data/analysis_results.csv"):
        self.output_path = Path(output_path)
        self.log_path = self.output_path.parent / "raw_data_srq2.log"
        self.logger = setup_logger("stats_manager")
        self._initialize_storage()

    def _initialize_storage(self):
        if not self.output_path.exists():
            df = pd.DataFrame(columns=CSV_COLUMNS)
            tmp = self.output_path.with_suffix(".tmp")
            df.to_csv(tmp, index=False)
            tmp.replace(self.output_path)
            self.logger.info(f"Dataset initialized: {self.output_path}")

    def save_metrics(self, project_id: str, metrics: dict):
        try:
            df = pd.read_csv(self.output_path)

            row = {
                "project_id": project_id,
                "node_count": metrics.get("node_count", 0),
                "edge_count": metrics.get("edge_count", 0),
                "density": metrics.get("density", 0.0),
                "max_depth": metrics.get("max_depth", 0),
                "is_dag": metrics.get("is_dag", False),
                "hubs": metrics.get("hubs", ""),
                "dep_count": metrics.get("dep_count", 0),
                "reflection_count": metrics.get("reflection_count", 0),
                "method_count": metrics.get("method_count", 0),
                "serializable_count": metrics.get("serializable_count", 0),
                "resources_count": metrics.get("resources_count", 0),
                "total_metadata": metrics.get("total_metadata", 0),
                "metadata_density": metrics.get("metadata_density", 0.0),
                "build_status": metrics.get("build_status", 0),
                "processed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            new_row = pd.DataFrame([row])

            if not df.empty and 'project_id' in df.columns:
                df = df[df['project_id'] != project_id]

            # concatenate
            df = pd.concat([df, new_row], ignore_index=True)

            # save
            tmp = self.output_path.with_suffix(".tmp")
            df.to_csv(tmp, index=False)
            tmp.replace(self.output_path)
            self.logger.info(f"[UPDATED] Metrics saved for {project_id}")

        except Exception as e:
            self.logger.error(f"Error when saving statistics: {e}")


    def compute_migration_metrics(self, graph_metrics: dict, aot_results: dict) -> dict:

        return {
            **graph_metrics,
            'dep_count': aot_results.get('dep_analysed_count', 0),
            'reflection_count': aot_results.get('reflection_total', 0),
            'method_count': aot_results.get('method_total', 0),
            'serializable_count': aot_results.get('serializable_total', 0),
            'resources_count': aot_results.get('resources_total', 0)
        }

    def save_raw_log(self, project_id, aot_results):

        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            with open(self.log_path, "a") as master_log:
                master_log.write(f"\n{'=' * 60}\n")
                master_log.write(f"PROJECT: {project_id} | DATE: {timestamp}\n")
                master_log.write(
                    f"SUMMARY: Reflection={aot_results.get('reflection_total', 0)} | "
                    f"Methods={aot_results.get('method_total', 0)} | "
                    f"Serializable={aot_results.get('serializable_total', 0)} | "
                    f"Resources={aot_results.get('resources_total', 0)} | "
                    f"Dependencies={aot_results.get('dep_analysed_count', 0)}\n"
                )
                master_log.write(f"{'-' * 60}\n")

                if aot_results.get('log_details'):
                    master_log.write("\n".join(aot_results['log_details']) + "\n")
                else:
                    master_log.write("No reachability metadata found for this topology.\n")

        except Exception as e:
            self.logger.error(f"Error saving raw log for {project_id}: {e}")