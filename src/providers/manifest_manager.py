# src/providers/manifest_manager.py

import pandas as pd
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional


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
            self.logger.error(f"Manifest not found: {self.file_path}")
            raise

    def _save(self):
        self.df.to_csv(self.file_path, index=False)

    def get_project_by_id(self, project_id: str) -> Optional[Dict[str, Any]]:
        project = self.df[self.df['project_id'] == project_id]
        return project.to_dict('records')[0] if not project.empty else None

    def get_pending_harvest(self) -> List[Dict[str, Any]]:
        mask = self.df['status'].str.upper().isin(['PENDING', '', 'NAN'])
        return self.df[mask].to_dict('records')

    def get_pending_analysis(self):
        """Projects that are already in S3 (HARVESTED) but have not been analyzed"""
        mask = self.df['status'].str.upper() == 'HARVESTED'
        return self.df[mask].to_dict('records')

    def update_project_status(self, project_id: str, status: str, s3_path: str = "", error: str = ""):
        """updates the csv"""
        index = self.df[self.df['project_id'] == project_id].index

        if not index.empty:
            idx = index[0]
            self.df.at[idx, 'status'] = status
            self.df.at[idx, 'last_attempt'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Only updates s3_path or error if they are provided (avoids erasing old data)
            if s3_path is not None:
                self.df.at[idx, 's3_path'] = s3_path

            if error is not None:
                self.df.at[idx, 'error_detail'] = error

            else:
                self.df.at[idx, 'error_detail'] = ""

            # save
            self._save()
            self.logger.info(f" [MANIFEST] {project_id} updated to {status}\n")