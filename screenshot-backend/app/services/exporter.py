import os
import shutil
from fastapi.responses import FileResponse
from config import UPLOAD_FOLDER

EXPORT_ZIP_NAME = "exported_photos.zip"

def export_photos():
    if os.path.exists(EXPORT_ZIP_NAME):
        os.remove(EXPORT_ZIP_NAME)

    shutil.make_archive("exported_photos", 'zip', UPLOAD_FOLDER)

    return FileResponse(
        path=EXPORT_ZIP_NAME,
        media_type='application/zip',
        filename=EXPORT_ZIP_NAME
    )
