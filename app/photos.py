from fastapi import APIRouter, UploadFile, File, HTTPException
from schemas.photo import PhotoUploadRequest, PhotoSearchRequest
from services.classifier import classify_photo
from services.searcher import search_photos
from services.deleter import delete_photo
from services.exporter import export_photos

router = APIRouter()

@router.post("/upload")
async def upload_photo(file: UploadFile = File(...)):
    return await classify_photo(file)

@router.post("/search")
async def search(request: PhotoSearchRequest):
    return search_photos(request)

@router.delete("/delete/{photo_id}")
async def delete(photo_id: str):
    return delete_photo(photo_id)

@router.get("/export")
async def export():
    return export_photos()
