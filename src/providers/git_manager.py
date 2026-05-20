# src/providers/git_manager.py

import subprocess
import shutil

from pathlib import Path
from src.interfaces.vcs import VersionControl
from src.utils.logger import setup_logger


class GitManager(VersionControl):
    def __init__(self):
        self.logger = setup_logger("git_manager")

    def _check_repo_exists(self, url: str) -> bool:
        """Check if the remote repository exists and is reachable."""
        try:
            result = subprocess.run(
                ["git", "ls-remote", url],
                check=True,
                capture_output=True,
                text=True,
                timeout=20
            )
            return True

        except subprocess.CalledProcessError:
            self.logger.error(f"Repository not reachable: {url}")
            return False

        except subprocess.TimeoutExpired:
            self.logger.error(f"Timeout checking repository: {url}")
            return False

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