# src/graph_processor.py

import os

from pathlib import Path
from src.providers.manifest_manager import ManifestManager
from src.providers.graph_manager import NetworkXGraphManager
from src.providers.reachability_metadata_manager import ReachabilityMetadataManager
from src.providers.s3_storage import S3Storage
from src.providers.stats_manager import StatsManager
from src.utils.logger import setup_logger


# What it does: It transforms the "lake" into graphs and calculates SRQ1 metrics.
# Focus: Network mathematics and topology.
# Result: Structural metrics (Centrality, Depth).
def run_analysis():
    logger = setup_logger()

    services = {
        'manifest': ManifestManager("data/manifest.csv"),
        'graph': NetworkXGraphManager(),
        'metadata': ReachabilityMetadataManager(logger=logger),
        'storage': S3Storage("graphaot-research"),
        'stats': StatsManager("data/analysis_results.csv"),
        'logger': logger
    }

    projects = services['manifest'].get_successful_projects()
    if not projects: return

    for project in projects:
        _process_project(project['project_id'], services)


def _process_project(p_id, service):
    logger = service['logger']
    logger.info(f">>> Processing: {p_id}")
    local_path = Path(f"temp/analysis_cache/{p_id}_bom.json")

    try:
        # Orchestration
        service['storage'].download_file(f"analysis/{p_id}/bom.json", str(local_path))
        graph = service['graph'].build_from_bom(str(local_path))

        metrics = service['graph'].get_metrics(graph)
        aot_results = service['metadata'].analyze_reachability_effort(graph, p_id)

        final_data = service['stats'].compute_migration_metrics(metrics, aot_results)
        service['stats'].save_metrics(p_id, final_data)
        service['stats'].save_raw_log(p_id, aot_results)

        logger.info(f" [OK] {p_id} completed.\n")
    except Exception as e:
        logger.error(f" [!] Error {p_id}: {e}\n")
    finally:
        if local_path.exists(): local_path.unlink()


if __name__ == "__main__":
    run_analysis()