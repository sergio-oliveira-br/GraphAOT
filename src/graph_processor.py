# src/graph_processor.py

import sys
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
def run_analysis(target_id=None):
    logger = setup_logger('graph_processor')

    BASE_DIR = Path(__file__).resolve().parent  # points to src/
    data_dir = BASE_DIR / "data"                  # src/data
    manifest_path = data_dir / "manifest.csv"
    results_csv = data_dir / "analysis_results.csv"

    services = {
        'manifest': ManifestManager(str(manifest_path)),
        'graph': NetworkXGraphManager(),
        'metadata': ReachabilityMetadataManager(logger=logger),
        'storage': S3Storage("graphaot-research"),
        'stats': StatsManager(str(results_csv)),
        'logger': logger
    }

    if target_id:
        logger.info(f"*** Manual Mode ***: Targeting project '{target_id}'")
        project = services['manifest'].get_project_by_id(target_id)
        projects = [project] if project else []
        if not projects:
            logger.error(f"Project '{target_id}' not found in manifest. Execution aborted.")
            return
    else:
        logger.info("*** Auto Mode ***: Fetching PENDING projects from manifest.")
        projects = services['manifest'].get_pending_analysis()

    if not projects:
        logger.info("Nothing to analyze at the moment.")
        return

    logger.info(f"--- Starting Graph Processor Pipeline: {len(projects)} projects ---")

    for project in projects:
        _process_project(project['project_id'], services)

    logger.info("--- Graph Processor Pipeline Finished ---")

def _process_project(p_id, service):
    logger = service['logger']
    logger.info(f">>> Processing: {p_id}")
    cache_dir = Path("temp/analysis_cache")
    cache_dir.mkdir(parents=True, exist_ok=True)
    local_path = cache_dir / f"{p_id}_bom.json"

    try:
        # Orchestration
        service['storage'].download_file(f"analysis/{p_id}/bom.json", str(local_path))

        graph = service['graph'].build_from_bom(str(local_path))
        metrics = service['graph'].get_metrics(graph)
        aot_results = service['metadata'].analyze_reachability_effort(graph, p_id)

        final_data = service['stats'].compute_migration_metrics(metrics, aot_results)
        service['stats'].save_metrics(p_id, final_data)
        service['stats'].save_raw_log(p_id, aot_results)

        service['manifest'].update_project_status(p_id, "ANALYSED")
        logger.info(f" [OK] {p_id} completed.\n")

    except Exception as e:
        logger.error(f" [!] Error {p_id}: {e}\n")
        service['manifest'].update_project_status(p_id, "FAILED_ANALYSIS", error=str(e))
        
    finally:
        if local_path.exists():
            local_path.unlink()
            logger.debug(f"Temporary file removed for {p_id}")

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else None
    run_analysis(target)