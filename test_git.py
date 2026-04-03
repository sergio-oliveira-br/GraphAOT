# test_git.py

from src.providers.git_manager import GitManager
import os

def test_clone():
    git = GitManager()
    target = "temp/test_repo"
    url = "https://github.com/CycloneDX/cyclonedx-maven-plugin.git"

    success = git.clone(url, target)

    if success and os.path.exists(target):
        print(f"Repository cloned successfully on{target}!")

    else:
        print("Failed to clone the repository.")


if __name__ == "__main__":
    test_clone()