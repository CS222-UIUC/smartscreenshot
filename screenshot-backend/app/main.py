from fastapi import FastAPI, UploadFile, File
from app.photos import save_upload_file
from app.vision import get_image_labels
from app.models.schemas import ScreenshotMetadata

import os
os.makedirs("uploaded_screenshots", exist_ok=True)

app = FastAPI()

@app.post("/upload/")
async def upload_screenshot(file: UploadFile = File(...)):
    path = save_upload_file(file)
    labels = get_image_labels(path)
    return {
        "filename": file.filename,
        "labels": labels
    }
