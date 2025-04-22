import os
import base64
import requests
from dotenv import load_dotenv
from services.photos_service import save_photo
from app.mongo_utils import insert_screenshot

load_dotenv()
GOOGLE_CLOUD_VISION_API_KEY = os.getenv("GOOGLE_CLOUD_VISION_API_KEY")

def call_google_vision_api(image_path: str):
    with open(image_path, "rb") as img_file:
        content = base64.b64encode(img_file.read()).decode("utf-8")

    url = f"https://vision.googleapis.com/v1/images:annotate?key={GOOGLE_CLOUD_VISION_API_KEY}"
    body = {
        "requests": [
            {
                "image": {"content": content},
                "features": [{"type": "LABEL_DETECTION", "maxResults": 5}]
            }
        ]
    }

    try:
        response = requests.post(url, json=body)
        response.raise_for_status()
        result = response.json()
        labels = result["responses"][0].get("labelAnnotations", [])
        return [label["description"] for label in labels]
    except Exception as e:
        print("Vision API error:", e)
        return []

async def classify_photo(file):
    filename = file.filename
    path = save_photo(file.file, filename)
    labels = call_google_vision_api(path)
    insert_screenshot({
        "filename": filename,
        "labels": labels
    })
    return {
        "message": "Upload successful",
        "filename": filename,
        "labels": labels
    }
