# src/dto/metrics_dto.py

from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import Optional, Dict, Any
from src.utils.hubs_serializer import HubsSerializer


@dataclass
class MetricsDTO:
    project_id: str

    # SRQ1
    node_count: Optional[int] = None
    edge_count: Optional[int] = None
    density: Optional[float] = None
    max_depth: Optional[int] = None
    is_dag: Optional[bool] = None
    hubs: Optional[str] = None
    degree_centrality_avg: float = 0.0
    betweenness_centrality_avg: float = 0.0
    closeness_centrality_avg: float = 0.0
    clustering_coeff_avg: float = 0.0
    transitive_ratio: float = 0.0

    # SRQ2
    dep_count: int = 0
    reflection_count: int = 0
    method_count: int = 0
    serializable_count: int = 0
    resources_count: int = 0
    total_metadata: int = 0
    metadata_density: float = 0.0

    # Build outcome
    build_status: int = 0
    processed_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    @classmethod
    def from_metrics(cls, project_id: str, metrics: Dict[str, Any]) -> "MetricsDTO":
        hubs_serialized = HubsSerializer().serialize(metrics.get("hubs"))
        dto_kwargs = {
            "project_id": project_id,
            "node_count": metrics.get("node_count"),
            "edge_count": metrics.get("edge_count"),
            "density": metrics.get("density"),
            "max_depth": metrics.get("max_depth"),
            "is_dag": metrics.get("is_dag"),
            "degree_centrality_avg": metrics.get("degree_centrality_avg", 0.0),
            "betweenness_centrality_avg": metrics.get("betweenness_centrality_avg", 0.0),
            "closeness_centrality_avg": metrics.get("closeness_centrality_avg", 0.0),
            "clustering_coeff_avg": metrics.get("clustering_coeff_avg", 0.0),
            "transitive_ratio": metrics.get("transitive_ratio", 0.0),
            "dep_count": metrics.get("dep_count", 0),
            "reflection_count": metrics.get("reflection_count", 0),
            "method_count": metrics.get("method_count", 0),
            "serializable_count": metrics.get("serializable_count", 0),
            "resources_count": metrics.get("resources_count", 0),
            "total_metadata": metrics.get("total_metadata", 0),
            "metadata_density": metrics.get("metadata_density", 0.0),
            "build_status": metrics.get("build_status", 0),
        }
        return cls(**dto_kwargs, hubs=hubs_serialized)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)