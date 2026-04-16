# src/data_collection.py

import shutil
from pathlib import Path
from src.providers.git_manager import GitManager
from src.providers.manifest_manager import ManifestManager
from src.providers.maven_manager import MavenManager
from src.providers.s3_storage import S3Storage
from src.utils.logger import setup_logger

BUCKET_NAME = "graphaot-research"
TEMP_DIR = Path("temp/work_dir")

# What does: "Collect" the raw data (Clone, Maven, S3).
# Focus: Infrastructure and extraction.
# Result: The "Data Lake" (bom.json, effective-pom.xml).
def run_harvester():
    logger = setup_logger()

    BASE_DIR = Path(__file__).resolve().parent.parent
    manifest_path = BASE_DIR / "src" / "data" / "manifest.csv"
    manifest = ManifestManager(str(manifest_path))

    services = {
        'manifest': manifest,
        'git': GitManager(),
        'maven': MavenManager(),
        'storage': S3Storage(BUCKET_NAME),
        'logger': logger
    }

    projects = services['manifest'].get_pending_projects()

    if not projects:
        logger.info("No pending projects found for harvesting.")
        return

    logger.info(f"--- Starting Harvester Pipeline: {len(projects)} projects ---")

    for project in projects:
        _harvest_single_project(project, services)

    logger.info("--- Harvester Pipeline Finished ---")

def _harvest_single_project(project: dict, service: dict):
    p_id = project['project_id']
    url = project['github_url']
    work_path = TEMP_DIR / p_id
    logger = service['logger']

    logger.info(f">>> Harvesting Project: {p_id}")

    try:
        # git
        if not service['git'].clone(url, work_path):
            service['manifest'].update_project_status(p_id, "FAILED_CLONE", error="Git clone failed")
            return

        # maven
        bom_file = service['maven'].generate_bom(work_path)
        audit_file = service['maven'].generate_audit_data(work_path)

        if not (bom_file and audit_file):
            service['manifest'].update_project_status(p_id, "FAILED_MAVEN", error="BOM/POM generation failed")
            return

        # S3
        s3_prefix = f"analysis/{p_id}"
        service['storage'].upload_file(bom_file, f"{p_id}/bom.json", "analysis")
        service['storage'].upload_file(audit_file, f"{p_id}/effective-pom.xml", "audit")

        # save
        s3_path_ref = f"s3://{BUCKET_NAME}/{s3_prefix}/"
        service['manifest'].update_project_status(p_id, "SUCCESS", s3_path=s3_path_ref)
        logger.info(f" [OK] {p_id} successfully stored in Lake.")

    except Exception as e:
        logger.error(f" [!] Critical error harvesting {p_id}: {str(e)}")
        service['manifest'].update_project_status(p_id, "CRITICAL_ERROR", error=str(e))

    finally:
        # Purge
        if work_path.exists():
            shutil.rmtree(work_path)
            logger.debug(f"Temporary files purged for {p_id}")

if __name__ == "__main__":
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    run_harvester()