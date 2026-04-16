# src/providers/stats_manager.py

import pandas as pd
import os
import logging

from pathlib import Path
from datetime import datetime
from src.interfaces.stats import StatsProvider

class StatsManager(StatsProvider):
    def __init__(self, output_path: str = "data/analysis_results.csv"):
        self.output_path = Path(output_path)
        self.log_path = self.output_path.parent / "raw_data_srq2.log"
        self.logger = logging.getLogger(__name__)
        self._initialize_storage()

    def _initialize_storage(self):
        if not os.path.exists(self.output_path):
            df = pd.DataFrame(columns=[
                'project_id',
                # SRQ1
                'node_count', 'edge_count', 'density', 'max_depth',
                'avg_clustering', 'is_dag', 'hubs',

                # SRQ2 - CMV
                'dep_count',
                'reflection_count', 'proxy_count', 'jni_count',
                'total_metadata',
                'metadata_density',

                # MDS
                'build_status',

                'processed_at'
            ])
            os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
            df.to_csv(self.output_path, index=False)
            print(f"Dataset initialized: {self.output_path}")

    def save_metrics(self, project_id: str, metrics: dict):
        try:
            df = pd.read_csv(self.output_path)

            new_data = {
                'project_id': project_id,

                # SRQ1
                'node_count': metrics.get('node_count'),
                'edge_count': metrics.get('edge_count'),
                'density': metrics.get('density'),
                'max_depth': metrics.get('max_depth'),
                'avg_clustering': metrics.get('avg_clustering'),
                'is_dag': metrics.get('is_dag'),
                'hubs': "|".join(metrics.get('top_hubs', [])) if isinstance(metrics.get('top_hubs'), list) else metrics.get('hubs'),

                # SRQ2
                'reflection_count': metrics.get('reflection_count', 0),
                'proxy_count': metrics.get('proxy_count', 0),
                'jni_count': metrics.get('jni_count', 0),
                'dep_count': metrics.get('dep_count', 0),
                'total_metadata': metrics.get('total_metadata', 0),
                'metadata_density': metrics.get('metadata_density', 0),

                # MDS
                'build_status': metrics.get('build_status', 0),

                'processed_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            # update
            if not df.empty and 'project_id' in df.columns:
                df = df[df['project_id'] != project_id]

            # concatenate
            df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)

            # save
            df.to_csv(self.output_path, index=False)
            self.logger.info(f" [CSV UPDATE] Metrics saved for {project_id} (CMV: {new_data['total_metadata']})")

        except Exception as e:
            self.logger.error(f"Error when saving statistics: {e}")

    @staticmethod
    def compute_migration_metrics(graph_metrics: dict, aot_results: dict) -> dict:

        reflection = aot_results.get('reflection_count', 0)
        proxy = aot_results.get('proxy_count', 0)
        jni = aot_results.get('jni_count', 0)
        deps = aot_results.get('dep_analysed_count', 0)

        total_cmv = reflection + proxy + jni
        metadata_density = total_cmv / deps if deps > 0 else 0

        return {
            **graph_metrics,
            'reflection_count': reflection,
            'proxy_count': proxy,
            'jni_count': jni,
            'dep_count': deps,
            'total_metadata': total_cmv,
            'metadata_density': metadata_density,
            'build_status': 0
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