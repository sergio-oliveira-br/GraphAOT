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
    "dep_count", "reflection_count","total_metadata", "metadata_density",
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
            dto = MetricsDTO.from_metrics(project_id, metrics)
            new_row = pd.DataFrame([dto.to_dict()])

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
        reflection = aot_results.get('reflection_count', 0)
        return {
            **graph_metrics,
            'reflection_count': reflection
        }

    def save_raw_log(self, project_id, aot_results):

        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            with open(self.log_path, "a") as master_log:
                master_log.write(f"\n{'=' * 60}\n")
                master_log.write(f"PROJECT: {project_id} | DATE: {timestamp}\n")
                master_log.write(
                    f"SUMMARY: {aot_results['dep_analysed_count']} deps | CMV: {aot_results['reflection_count'] + aot_results['proxy_count'] + aot_results['jni_count']}\n"
                )
                master_log.write(f"{'-' * 60}\n")

                if aot_results.get('log_details'):
                    master_log.write("\n".join(aot_results['log_details']) + "\n")
                else:
                    master_log.write("No reachability metadata found for this topology.\n")

        except Exception as e:
            self.logger.error(f"Error saving raw log for {project_id}: {e}")