from pydantic import BaseModel, EmailStr
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str
    user: dict

class TokenData(BaseModel):
    username: Optional[str] = None

class User(BaseModel):
    id: str
    email: EmailStr
    name: str
    role: str = "user"
    is_active: bool = True

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    role: str = "user"

class UserInDB(User):
    hashed_password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str