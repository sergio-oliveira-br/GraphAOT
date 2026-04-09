# src/graph_processor.py

import os

from pathlib import Path
from src.providers.manifest_manager import ManifestManager
from src.providers.graph_manager import NetworkXGraphManager
from src.providers.reachability_metadata_manager import ReachabilityMetadataManager
from src.providers.s3_storage import S3Storage
from src.providers.stats_manager import StatsManager
from datetime import datetime


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
    metadata_service = ReachabilityMetadataManager()

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

            # metadata effort
            aot_results = analyze_reachability_effort(graph, metadata_service, p_id)

            # calculation
            final_data = stats_service.compute_migration_metrics(metrics, aot_results)

            stats_service.save_log(p_id, aot_results, base_path="src/data")

            # data persistence
            stats_service.save_metrics(p_id, final_data)

            # save the logs
            if aot_results['log_details']:
                with open(f"temp/analysis_cache/{p_id}_aot_details.txt", "w") as f:
                    f.write("\n".join(aot_results['log_details']))

            print(f" [OK] Data saved: {p_id}")

            # cleanup
            if local_temp_path.exists():
                local_temp_path.unlink()

        except Exception as e:
            print(f" [!] Error processing {p_id}: {e}")


def analyze_reachability_effort(graph, metadata_service, project_id):

    total_refl = 0
    total_proxy = 0
    total_jni = 0
    dep_count = 0
    details = []

    print(f"--- [DETAILED ANALYSIS: {project_id}] ---")

    for node, data in graph.nodes(data=True):
        if data.get('type') == 'dependency':
            dep_count += 1

            group = data.get('group', 'unknown')
            artifact = data.get('name', '') or data.get('artifact', 'unknown')
            version = data.get('version', '0.0.0')

            meta = metadata_service.get_metadata_volume(group, artifact, version)

            total_refl += meta.get('reflection', 0)
            total_proxy += meta.get('proxy', 0)
            total_jni += meta.get('jni', 0)

            if any(v > 0 for v in meta.values()):
                line = f"Dependency: {artifact}:{version} | Refl: {meta['reflection']} | Proxy: {meta['proxy']}"
                print(f"   [+] {line}")
                details.append(line)

    print(f"--- [END OF ANALYSIS: {dep_count} deps processed] ---\n")

    return {
        "reflection_count": total_refl,
        "proxy_count": total_proxy,
        "jni_count": total_jni,
        "dep_analysed_count": dep_count,
        "log_details": details
    }

if __name__ == "__main__":
    run_analysis()