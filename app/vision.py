import requests
import base64
from app.config import GOOGLE_CLOUD_VISION_API_KEY

def get_image_labels(image_path: str):
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

    response = requests.post(url, json=body)
    result = response.json()
    labels = result["responses"][0].get("labelAnnotations", [])
    return [label["description"] for label in labels]
