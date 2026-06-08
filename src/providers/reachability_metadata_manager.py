# src/providers/reachability_metadata_manager.py

import requests

from typing import Tuple, Dict, Optional, List
from src.interfaces.metadata import MetadataProvider
from src.utils.logger import setup_logger


def _compute_counts(data: dict) -> Dict[str, int]:
    if not data:
        return {"reflection_count": 0, "method_count": 0, "serializable_count": 0, "resources_count": 0}

    reflection_entries = data.get("reflection", [])
    resources_entries = data.get("resources", [])

    reflection_count = len(reflection_entries)
    method_count = sum(len(entry.get("methods", [])) for entry in reflection_entries)
    serializable_count = sum(1 for entry in reflection_entries if entry.get("serializable"))
    resources_count = len(resources_entries)

    return {
        "reflection_count": reflection_count,
        "method_count": method_count,
        "serializable_count": serializable_count,
        "resources_count": resources_count
    }


def _dependency_nodes(graph):
    for node, data in graph.nodes(data=True):
        if data.get('type') == 'dependency':
            yield data


def _select_target(index: List[dict], version: str) -> Optional[str]:
    """Choose the appropriate metadata-version of the index"""
    if not index:
        return None
    target = next((e["metadata-version"] for e in index if version in e.get("tested-versions", [])), None)
    if target:
        return target
    target = next((e["metadata-version"] for e in index if e.get("latest")), None)
    return target


def _normalize_coords(group: str, artifact: str, version: str) -> Tuple[str, str, str]:
    """Cleans and normalizes group, artifact, and version"""
    g = group.replace("pkg:maven/", "").split('?')[0]
    a = artifact.split('@')[0].split('?')[0]
    v = str(version).strip()
    return g, a, v


class ReachabilityMetadataManager(MetadataProvider):
    def __init__(self):
        self.base_url = "https://raw.githubusercontent.com/oracle/graalvm-reachability-metadata/master/metadata"
        self.logger = setup_logger('reachability-metadata-manager')
        self.timeout = 8

    def _fetch_index(self, g: str, a: str) -> Optional[List[dict]]:
        """Downloads the index.json"""
        try:
            resp = requests.get(f"{self.base_url}/{g}/{a}/index.json", timeout=self.timeout)
            if resp.status_code == 200:
                return resp.json()
            self.logger.debug(f"Metadata index not found for {g}:{a} (status {resp.status_code})")
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Network error fetching index for {a}: {e}")
        return None

    def _fetch_metadata(self, g: str, a: str, target: str) -> Optional[dict]:
        """Download reachability-metadata.json from the target"""
        try:
            resp = requests.get(f"{self.base_url}/{g}/{a}/{target}/reachability-metadata.json", timeout=self.timeout)
            if resp.status_code == 200:
                return resp.json()
            self.logger.debug(f"Metadata file not found for {g}:{a} target {target}")
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Network error fetching metadata for {a}: {e}")
        return None

    def _process_dependency(self, data: dict) -> Tuple[Dict[str, int], Optional[str]]:
        group = data.get('group', 'unknown')
        artifact = data.get('name', '') or data.get('artifact', 'unknown')
        version = data.get('version', '0.0.0')

        meta = self.get_metadata_volume(group, artifact, version)

        if any(v > 0 for v in meta.values()):
            line = (
                f"Dependency: {artifact}:{version} | "
                f"Refl: {meta['reflection_count']} | "
                f"Methods: {meta['method_count']} | "
                f"Serializable: {meta['serializable_count']} | "
                f"Resources: {meta['resources_count']}"
            )
            return meta, line

        return meta, None


    def get_metadata_volume(self, group: str, artifact: str, version: str) -> dict:
        res_default = {"reflection": 0,
                       "method_count": 0,
                       "serializable_count": 0,
                       "resources_count": 0
                       }

        g, a, v = _normalize_coords(group, artifact, version)

        index = self._fetch_index(g, a)
        if not index:
            return res_default

        target = _select_target(index, v)
        if not target:
            return res_default

        data = self._fetch_metadata(g, a, target)
        if not data:
            return res_default

        return _compute_counts(data)


    def analyze_reachability_effort(self, graph, project_id):
        total_refl = 0
        total_methods = 0
        total_serializable = 0
        total_resources = 0
        dep_count = 0
        details = []

        self.logger.info(f"--- [START ANALYSIS: {project_id}] ---")

        for data in _dependency_nodes(graph):
            dep_count += 1
            meta, line = self._process_dependency(data)

            total_refl += meta.get('reflection_count', 0)
            total_methods += meta.get('method_count', 0)
            total_serializable += meta.get('serializable_count', 0)
            total_resources += meta.get('resources_count', 0)

            if line:
                self.logger.info(f"[+] {line}")
                details.append(line)

        self.logger.info(f"--- [END OF ANALYSIS: {dep_count} deps processed for {project_id}] ---")

        return {
            "reflection_total": total_refl,
            "method_total": total_methods,
            "serializable_total": total_serializable,
            "resources_total": total_resources,
            "dep_analysed_count": dep_count,
            "log_details": details
        }