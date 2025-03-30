import shutil
from fastapi import UploadFile

UPLOAD_DIR = "uploaded_screenshots"

def save_upload_file(file: UploadFile) -> str:
    path = f"{UPLOAD_DIR}/{file.filename}"
    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return path
