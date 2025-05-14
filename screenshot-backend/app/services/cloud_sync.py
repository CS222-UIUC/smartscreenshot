import os
from typing import Optional, List
from app.db.mongo_utils import get_screenshots_by_category, get_screenshots

class CloudSync:
    def __init__(self, provider: str):
        self.provider = provider
        if provider == "gcs":
            try:
                from google.cloud import storage
                self.client = storage.Client()
            except ImportError:
                raise ValueError("Google Cloud Storage is not installed. Please install google-cloud-storage package.")
        else:
            raise ValueError(f"Unsupported cloud provider: {provider}")

    def sync_screenshots(self, user_id: str, category: Optional[str] = None, bucket_name: str = None) -> dict:
        """Sync screenshots to cloud storage"""
        if not bucket_name:
            bucket_name = f"screenshot-sorter-{user_id}"

        # Get screenshots
        if category:
            screenshots, _ = get_screenshots_by_category(user_id, category)
        else:
            screenshots = get_screenshots(user_id)

        # Create bucket if it doesn't exist
        try:
            bucket = self.client.get_bucket(bucket_name)
        except Exception:
            bucket = self.client.create_bucket(bucket_name)

        # Upload files
        results = {
            "success": [],
            "failed": []
        }

        for screenshot in screenshots:
            try:
                if os.path.exists(screenshot["file_path"]):
                    blob = bucket.blob(f"{category or 'all'}/{screenshot['filename']}")
                    blob.upload_from_filename(screenshot["file_path"])
                    results["success"].append(screenshot["filename"])
                else:
                    results["failed"].append({
                        "filename": screenshot["filename"],
                        "error": "File not found"
                    })
            except Exception as e:
                results["failed"].append({
                    "filename": screenshot["filename"],
                    "error": str(e)
                })

        return results 