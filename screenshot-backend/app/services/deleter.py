import os
from config import UPLOAD_FOLDER
from app.mongo_utils import delete_screenshot

def delete_photo(photo_id: str):
    file_path = os.path.join(UPLOAD_FOLDER, photo_id)

    file_deleted = False
    if os.path.exists(file_path):
        os.remove(file_path)
        file_deleted = True

    mongo_deleted = delete_screenshot(photo_id)

    return {
        "message": f"Deleted: {photo_id}",
        "file_deleted": file_deleted,
        "mongo_deleted_count": mongo_deleted
    }
