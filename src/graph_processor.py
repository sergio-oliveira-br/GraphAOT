# src/graph_processor.py

from pathlib import Path
from src.providers.manifest_manager import ManifestManager
from src.providers.graph_manager import NetworkXGraphManager
from src.providers.s3_storage import S3Storage
from src.providers.stats_manager import StatsManager


# What it does: It transforms the "lake" into graphs and calculates SRQ1 metrics.
# Focus: Network mathematics and topology.
# Result: Structural metrics (Centrality, Depth).
def run_analysis():

    # 1. Setup
    manifest = ManifestManager("data/manifest.csv")
    graph_service = NetworkXGraphManager()
    BUCKET_NAME = "graphaot-research"
    storage = S3Storage(BUCKET_NAME)
    stats_service = StatsManager("data/analysis_results.csv")

    # 2. Upload only projects that have been SUCCESSFUL
    projects = manifest.get_successful_projects()

    if not projects:
        print("No project with 'SUCCESS' status found in the manifest.")
        return

    for project in projects:
        p_id = project['project_id']
        local_temp_path = Path(f"temp/analysis_cache/{p_id}_bom.json")
        local_temp_path.parent.mkdir(parents=True, exist_ok=True)

        print(f"\n>>> Processing Topology: {p_id}")

        try:
            # download and build
            storage.download_file(f"analysis/{p_id}/bom.json", str(local_temp_path))
            graph = graph_service.build_from_bom(str(local_temp_path))

            # extracting metrics
            metrics = graph_service.get_metrics(graph)

            # data Persistence
            stats_service.save_metrics(p_id, metrics)

            print(f" [V] Data saved: {p_id}")

            # cleanup
            if local_temp_path.exists():
                local_temp_path.unlink()

        except Exception as e:
            print(f" [!] Error processing {p_id}: {e}")

if __name__ == "__main__":
    run_analysis()