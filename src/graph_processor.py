# src/graph_processor.py

from pathlib import Path

from src.providers.manifest_manager import ManifestManager
from src.providers.graph_manager import NetworkXGraphManager
from src.providers.s3_storage import S3Storage


# What it does: It transforms the "lake" into graphs and calculates SRQ1 metrics.
# Focus: Network mathematics and topology.
# Result: Structural metrics (Centrality, Depth).
def run_analysis():

    # 1. Setup
    manifest = ManifestManager("/Users/sergiovinicio/PycharmProjects/GraphAOT/data/manifest.csv")
    graph_service = NetworkXGraphManager()
    BUCKET_NAME = "graphaot-research"
    storage = S3Storage(BUCKET_NAME)

    # 2. Upload only projects that have been SUCCESSFUL
    projects = manifest.get_successful_projects()

    if not projects:
        print("No project with 'SUCCESS' status found in the manifest.")
        return

    for project in projects:
        p_id = project['project_id']

        # 1. temp save
        local_temp_path = Path(f"temp/analysis_cache/{p_id}_bom.json")
        local_temp_path.parent.mkdir(parents=True, exist_ok=True)

        print(f">>> Downloading BOM from S3: {p_id}")
        s3_key = f"analysis/{p_id}/bom.json"

        try:
            storage.download_file(s3_key, str(local_temp_path))

            # 3. Build Graph
            graph = graph_service.build_from_bom(str(local_temp_path))
            metrics = graph_service.get_metrics(graph)

            print(f"[OK] Project {p_id} ")
            print(f"  > Structure: {metrics['node_count']} node | Max Depth: {metrics['max_depth']}")
            print(f"  > Critical Hubs: {', '.join(metrics['top_hubs'])}")
            print(f"  > Density: {metrics['density']:.4f}")
            print("-" * 50)

            # 4. cleanup
            local_temp_path.unlink()

        except Exception as e:
            print(f" [!] Error processing {p_id}: {e}")

if __name__ == "__main__":
    run_analysis()