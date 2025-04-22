import os
import shutil
from fastapi import UploadFile

UPLOAD_DIR = "uploaded_screenshots"

def save_upload_file(upload_file: UploadFile) -> str:
    """Save an uploaded file and return its path"""
    file_path = os.path.join(UPLOAD_DIR, upload_file.filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
    
    return file_path

def delete_upload_file(file_path: str):
    """Delete an uploaded file"""
    if os.path.exists(file_path):
        os.remove(file_path)