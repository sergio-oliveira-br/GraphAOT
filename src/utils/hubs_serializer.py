# src/utils/hubs_serializer.py

from typing import Optional, List, Any
from src.utils.logger import setup_logger

class HubsSerializer:
    def __init__(self, sep: str = "|", logger=None):
        self.sep = sep
        # usa logger injetado ou cria um logger padrão do serviço utilitário
        self.logger = logger or setup_logger("hubs_serializer")

    def serialize(self, hubs: Any) -> Optional[str]:
        normalized = self._normalize_to_list(hubs)
        if not normalized:
            return None
        return self.sep.join(map(str, normalized))

    def _normalize_to_list(self, hubs: Any) -> List[str]:
        if hubs is None:
            return []

        if isinstance(hubs, str):
            return [hubs]

        if isinstance(hubs, (list, tuple, set)):
            return [str(x) for x in hubs if x is not None]

        if isinstance(hubs, dict):
            candidate = hubs.get("hubs") or hubs.get("top_hubs")

            if isinstance(candidate, (list, tuple, set)):
                return [str(x) for x in candidate if x is not None]

            if isinstance(candidate, str):
                return [candidate]
            self.logger.debug("HubsSerializer: dict provided but no usable 'hubs' found.")
            return []

        try:
            return [str(hubs)]

        except Exception:
            self.logger.debug("HubsSerializer: unable to coerce hubs to string", exc_info=True)
            return []
