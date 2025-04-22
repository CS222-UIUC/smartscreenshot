from pydantic import BaseModel
from typing import List, Optional

class PhotoUploadRequest(BaseModel):
    filename: str
    labels: List[str]

class PhotoSearchRequest(BaseModel):
    query: str
