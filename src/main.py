# src/main.py

import shutil
from pathlib import Path
from src.providers.git_manager import GitManager
from src.providers.manifest_manager import ManifestManager
from src.providers.maven_manager import MavenManager
from src.providers.s3_storage import S3Storage
from src.utils.logger import setup_logger

BUCKET_NAME = "graphaot-research"
TEMP_DIR = Path("temp/work_dir")


def run_harvester():

    logger = setup_logger()
    manifest = ManifestManager("../data/manifest.csv")
    git = GitManager()
    mvn = MavenManager()
    storage = S3Storage(BUCKET_NAME)

    # load the csv manifest
    projects = manifest.get_pending_projects()
    logger.info(f"Starting processing of {len(projects)} projects.")

    for project in projects:
        p_id = project['project_id']
        url = project['github_url']

        project_path = TEMP_DIR / p_id
        logger.info(f">>> Processando: {p_id}")

        try:
            if git.clone(url, project_path):

                #Step B: Maven (mining)
                bom_file = mvn.generate_bom(project_path)
                audit_file = mvn.generate_audit_data(project_path)

                if bom_file and audit_file:
                    # Step C: S3
                    s3_path = f"s3://{BUCKET_NAME}/analysis/{p_id}/"
                    storage.upload_file(bom_file, f"{p_id}/bom.json", "analysis")
                    storage.upload_file(audit_file, f"{p_id}/effective-pom.xml", "audit")

                    manifest.update_project_status(p_id, "SUCCESS", s3_path=s3_path)

                else:
                    manifest.update_project_status(p_id, "FAILED_MAVEN", error="BOM or POM generation failed")
            else:
                manifest.update_project_status(p_id, "FAILED_CLONE", error="Git clone timed out or failed")

        except Exception as e:
            logger.error(f"Critical error in the project {p_id}: {str(e)}")
            manifest.update_project_status(p_id, "CRITICAL_ERROR", error=str(e))

        finally:
            # Step D: Purge
            if Path(project_path).exists():
                shutil.rmtree(project_path)
                logger.info(f"Purge completed: {p_id}")

if __name__ == "__main__":
    run_harvester()