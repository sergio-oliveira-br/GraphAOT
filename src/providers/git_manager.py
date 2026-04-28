# src/providers/git_manager.py

import subprocess
import logging
import shutil
from pathlib import Path
from src.interfaces.vcs import VersionControl
from src.utils.logger import setup_logger


class GitManager(VersionControl):
    def __init__(self):
        self.logger = setup_logger("git_manager")

    def clone(self, url: str, target_path: str) -> bool:
        """Performs the ephemeral clone (depth 1)"""
        path = Path(target_path)

        # If the folder already exists, it is removed earlier
        if path.exists():
            shutil.rmtree(path)

        try:
            self.logger.info(f"Cloning repository: {url}")
            # --depth 1: Download only the last commit
            result = subprocess.run(
                ["git", "clone", "--depth", "1", url, target_path],
                check=True,
                capture_output=True,
                text=True,
                timeout=120  # 2 min
            )
            return True

        except subprocess.TimeoutExpired:
            self.logger.error(f"Timeout when cloning {url}")
            return False

        except subprocess.CalledProcessError as e:
            self.logger.error(f"Git Clone error: {e.stderr}")
            return False

        except Exception as e:
            self.logger.error(f"Unexpected error in Git: {str(e)}")
            return False