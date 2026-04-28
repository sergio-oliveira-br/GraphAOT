# src/providers/maven_manager.py

import subprocess
import shutil

from pathlib import Path
from src.interfaces.build import BuildTool
from src.utils.logger import setup_logger


class MavenManager(BuildTool):
    def __init__(self, executable_path: str = None):
        self.logger = setup_logger("maven_manager")
        self.mvn_bin = executable_path or shutil.which("mvn") or "/opt/homebrew/bin/mvn"

        if not Path(self.mvn_bin).exists():
            self.logger.warning(f"Warning: Maven executable not found in {self.mvn_bin}")

    def _run_mvn(self, project_path: str, args: list) -> bool:
        """Setting memory limit for the Maven JVM"""
        try:
            env = {"MAVEN_OPTS": "-Xmx2g -Xms512m"}
            cmd = [self.mvn_bin] + args + ["-f", project_path, "-DskipTests", "-q"]

            self.logger.info(f"Running Maven: {' '.join(args)}")
            subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=300, env=env)
            return True

        except subprocess.CalledProcessError as e:
            self.logger.error(f"Maven error: {e.stderr}")
            return False

        except subprocess.TimeoutExpired:
            self.logger.error(f"Timeout: Mvn build exceeded 5 minutes.{project_path}")
            return False

    def generate_bom(self, project_path: str) -> str:
        """Run CycloneDX"""
        target_file = Path(project_path) / "target" / "bom.json"

        # Command to generate the aggregate BOM
        success = self._run_mvn(project_path, ["org.cyclonedx:cyclonedx-maven-plugin:makeAggregateBom"])
        return str(target_file) if success and target_file.exists() else ""

    def generate_audit_data(self, project_path: str) -> str:
        """Generate the POM"""

        target_dir = Path(project_path) / "target"
        target_dir.mkdir(parents=True, exist_ok=True)

        output_file = target_dir / "effective-pom.xml"

        args = ["help:effective-pom", f"-Doutput={output_file.absolute()}"]

        success = self._run_mvn(project_path, args)

        if success and output_file.exists():
            return str(output_file)

        self.logger.error(f"Audit file not found in: {output_file}")
        return ""