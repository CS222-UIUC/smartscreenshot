from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class FolderCreate(BaseModel):
    name: str
    description: Optional[str] = None
    parent_id: Optional[str] = None

class Folder(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    parent_id: Optional[str] = None
    user_id: str
    created_at: datetime
    updated_at: datetime
    screenshot_count: int = 0 