# test_s3.py
from src.providers.s3_storage import S3Storage

BUCKET = "graphaot-research"

def test_connection():
    storage = S3Storage(BUCKET)

    with open("dummy.json", "w") as f:
        f.write('{"status": "test"}')

    success = storage.upload_file("dummy.json", "test-project/bom.json", "analysis")

    if success:
        print("Connection to S3 established successfully!")
    else:
        print("Connection failed.")

if __name__ == "__main__":
    test_connection()