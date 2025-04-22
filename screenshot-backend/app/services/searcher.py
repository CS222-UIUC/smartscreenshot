from app.mongo_utils import find_screenshots
from schemas.photo import PhotoSearchRequest

def search_photos(request: PhotoSearchRequest):
    query = request.query
    filter = {"labels": {"$regex": query, "$options": "i"}}  

    results = find_screenshots(filter)
    return [
        {
            "filename": doc["filename"],
            "labels": doc.get("labels", [])
        }
        for doc in results
    ]
