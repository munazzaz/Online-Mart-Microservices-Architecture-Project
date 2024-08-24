from pydantic import BaseModel
from typing import Optional
from sqlmodel import Field, SQLModel
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    class Config:
        orm_mode = True

class UserUpdate(BaseModel):
    email: Optional[str] = None
    password: Optional[str] = None


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None



class UserOut(BaseModel):
    username: str
    email: str

    class Config:
        from_attributes = True




class RefreshToken(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    token: str
    expires_at: datetime