# src/providers/reachability_metadata_manager.py

import requests
from src.interfaces.metadata import MetadataProvider

class ReachabilityMetadataManager(MetadataProvider):
    def __init__(self):
        self.base_url = "https://raw.githubusercontent.com/oracle/graalvm-reachability-metadata/master/metadata"

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

        except Exception:
            pass

        return res_default