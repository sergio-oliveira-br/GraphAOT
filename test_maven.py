# test_maven.py

from src.providers.maven_manager import MavenManager
import os

def test_maven_extraction():
    mvn = MavenManager()
    project_path = "temp/test_repo"

    if not os.path.exists(project_path):
        print("Error: Project folder not found.")
        return

    print("Generating Maven artifacts...")

    bom_path = mvn.generate_bom(project_path)
    audit_path = mvn.generate_audit_data(project_path)

    if bom_path and os.path.exists(bom_path):
        print(f"SBOM generated successfully: {bom_path}")
    else:
        print("Failed to generate SBOM.")

    if audit_path and os.path.exists(audit_path):
        print(f"POM generated successfully: {audit_path}")
    else:
        print("Failed to generate POM")


if __name__ == "__main__":
    test_maven_extraction()