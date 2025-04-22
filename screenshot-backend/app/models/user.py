from pydantic import BaseModel
from typing import Optional

class UserBase(BaseModel):
    username: str
    is_active: bool = True

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: str
    hashed_password: str

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None 