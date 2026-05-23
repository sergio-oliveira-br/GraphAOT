# src/dto/metrics_dto.py

from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import Optional, List, Dict, Any

def _serialize_hubs(metrics: Dict[str, Any]) -> Optional[str]:
    hubs = metrics.get("top_hubs")
    if isinstance(hubs, list):
        return "|".join(map(str, hubs))
    return metrics.get("hubs")

@dataclass
class MetricsDTO:
    project_id: str
    node_count: Optional[int] = None
    edge_count: Optional[int] = None
    density: Optional[float] = None
    max_depth: Optional[int] = None
    is_dag: Optional[bool] = None
    hubs: Optional[str] = None
    dep_count: int = 0
    reflection_count: int = 0
    total_metadata: int = 0
    metadata_density: float = 0.0
    build_status: int = 0
    processed_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    @classmethod
    def from_metrics(cls, project_id: str, metrics: Dict[str, Any]) -> "MetricsDTO":
        dto_kwargs = {
            "project_id": project_id,
            "node_count": metrics.get("node_count"),
            "edge_count": metrics.get("edge_count"),
            "density": metrics.get("density"),
            "max_depth": metrics.get("max_depth"),
            "is_dag": metrics.get("is_dag"),
            "hubs": _serialize_hubs(metrics),
            "reflection_count": metrics.get("reflection_count", 0),
            "dep_count": metrics.get("dep_count", 0),
            "total_metadata": metrics.get("total_metadata", 0),
            "metadata_density": metrics.get("metadata_density", 0.0),
            "build_status": metrics.get("build_status", 0),
        }
        return cls(**dto_kwargs)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)