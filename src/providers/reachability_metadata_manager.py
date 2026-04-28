# src/providers/reachability_metadata_manager.py
import logging
import requests

from src.interfaces.metadata import MetadataProvider
from src.utils.logger import setup_logger


class ReachabilityMetadataManager(MetadataProvider):
    def __init__(self):
        self.base_url = "https://raw.githubusercontent.com/oracle/graalvm-reachability-metadata/master/metadata"
        self.logger = setup_logger('reachability-metadata-manager')

    def get_metadata_volume(self, group: str, artifact: str, version: str) -> dict:
        """Fetches the official Oracle repository"""

        # cleanup
        g = group.replace("pkg:maven/", "").split('?')[0]
        a = artifact.split('@')[0].split('?')[0]
        v = str(version).strip()

        res_default = {"reflection": 0, "proxy": 0, "jni": 0}

        try:
            resp = requests.get(f"{self.base_url}/{g}/{a}/index.json", timeout=5)
            if resp.status_code != 200:
                self.logger.debug(f"Metadata index not found for {g}:{a}")
                return res_default

            index = resp.json()
            target = next((e["metadata-version"] for e in index if v in e.get("tested-versions", [])), None)

            if not target:
                target = next((e["metadata-version"] for e in index if e.get("latest")), None)

            if not target:
                return res_default

            meta_resp = requests.get(f"{self.base_url}/{g}/{a}/{target}/reachability-metadata.json", timeout=5)
            if meta_resp.status_code == 200:
                data = meta_resp.json()
                return {
                    "reflection": len(data.get("reflection", [])),
                    "jni": len(data.get("jni", [])),
                    "proxy": len(data.get("proxy", []))
                }

        except requests.exceptions.RequestException as e:
            self.logger.warning(f"Network error fetching metadata for {a}: {e}")

        except Exception as e:
            self.logger.error(f"Unexpected error in MetadataManager: {e}")

        return res_default


    def analyze_reachability_effort(self, graph, project_id):

        total_refl = 0
        total_proxy = 0
        total_jni = 0
        dep_count = 0
        details = []

        self.logger.info(f"--- [START ANALYSIS: {project_id}] ---")

        for node, data in graph.nodes(data=True):
            if data.get('type') == 'dependency':
                dep_count += 1

                group = data.get('group', 'unknown')
                artifact = data.get('name', '') or data.get('artifact', 'unknown')
                version = data.get('version', '0.0.0')

                meta = self.get_metadata_volume(group, artifact, version)

                total_refl += meta.get('reflection', 0)
                total_proxy += meta.get('proxy', 0)
                total_jni += meta.get('jni', 0)

                if any(v > 0 for v in meta.values()):
                    line = f"Dependency: {artifact}:{version} | Refl: {meta['reflection']} | Proxy: {meta['proxy']}"
                    self.logger.info(f"[+] {line}")
                    details.append(line)

        self.logger.info(f"--- [END OF ANALYSIS: {dep_count} deps processed for {project_id}] ---")

        return {
            "reflection_count": total_refl,
            "proxy_count": total_proxy,
            "jni_count": total_jni,
            "dep_analysed_count": dep_count,
            "log_details": details
        }
