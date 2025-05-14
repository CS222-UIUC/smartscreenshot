import os
import shutil
import json
from datetime import datetime
from typing import List, Optional
from fastapi.responses import FileResponse
from app.db.mongo_utils import get_screenshots_by_category, get_screenshots

EXPORT_DIR = "exports"
os.makedirs(EXPORT_DIR, exist_ok=True)

def create_export_zip(category: Optional[str], user_id: str) -> str:
    """Create a zip file containing screenshots for a specific category"""
    # Create temporary directory for export
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    export_name = f"export_{category or 'all'}_{timestamp}"
    export_path = os.path.join(EXPORT_DIR, export_name)
    os.makedirs(export_path, exist_ok=True)

    # Get screenshots
    if category:
        screenshots, _ = get_screenshots_by_category(user_id, category)
    else:
        screenshots = get_screenshots(user_id)

    # Copy files to export directory
    for screenshot in screenshots:
        if os.path.exists(screenshot["file_path"]):
            shutil.copy2(
                screenshot["file_path"],
                os.path.join(export_path, screenshot["filename"])
            )

    # Create zip file
    zip_path = f"{export_path}.zip"
    shutil.make_archive(export_path, 'zip', export_path)
    
    # Clean up temporary directory
    shutil.rmtree(export_path)
    
    return zip_path

def export_metadata(category: Optional[str], user_id: str, format: str = "json") -> str:
    """Export screenshot metadata in specified format"""
    # Get screenshots
    if category:
        screenshots, _ = get_screenshots_by_category(user_id, category)
    else:
        screenshots = get_screenshots(user_id)

    # Create metadata file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    export_name = f"metadata_{category or 'all'}_{timestamp}"
    
    if format == "json":
        file_path = os.path.join(EXPORT_DIR, f"{export_name}.json")
        with open(file_path, "w") as f:
            json.dump(screenshots, f, indent=2)
    elif format == "csv":
        file_path = os.path.join(EXPORT_DIR, f"{export_name}.csv")
        with open(file_path, "w") as f:
            f.write("filename,description,category,created_at,tags\n")
            for s in screenshots:
                tags = ",".join(s.get("vision_tags", []))
                f.write(f"{s['filename']},{s.get('description', '')},{s.get('category', '')},{s['created_at']},{tags}\n")
    
    return file_path 