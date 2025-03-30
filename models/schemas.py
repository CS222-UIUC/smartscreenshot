from pydantic import BaseModel
from typing import Optional

class ScreenshotMetadata(BaseModel):
    filename: str
    category: Optional[str] = None
    description: Optional[str] = None
