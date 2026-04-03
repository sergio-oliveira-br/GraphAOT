# src/providers/manifest_manager.py

import pandas as pd
import logging
from datetime import datetime
from typing import List, Dict, Any


class ManifestManager:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.logger = logging.getLogger(__name__)
        self.df = self._load_manifest()

    def _load_manifest(self) -> pd.DataFrame:
        """Load CSV"""
        try:
            return pd.read_csv(self.file_path, dtype=str).fillna("")

        except FileNotFoundError:
            self.logger.error(f"Manifesto not found: {self.file_path}")
            raise

    def get_pending_projects(self) -> List[Dict[str, Any]]:
        """Returns a list of dictionaries"""
        mask = self.df['status'].str.upper().isin(['', 'NAN', 'PENDING'])
        pending = self.df[mask]
        return pending.to_dict('records')

    def update_project_status(self, project_id: str, status: str, s3_path: str = "", error: str = ""):
        """updates the csv"""
        index = self.df[self.df['project_id'] == project_id].index

        if not index.empty:
            idx = index[0]
            self.df.at[idx, 'status'] = status
            self.df.at[idx, 's3_path'] = s3_path
            self.df.at[idx, 'error_detail'] = error
            self.df.at[idx, 'last_attempt'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # save
            self.df.to_csv(self.file_path, index=False)
            self.logger.info(f"Status atualizado para {project_id}: {status}")

    def get_successful_projects(self) -> list:
        """Returns only successful projects"""
        mask = self.df['status'].str.upper() == 'SUCCESS'
        successful = self.df[mask]
        return successful.to_dict('records')