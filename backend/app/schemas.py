from pydantic import BaseModel, EmailStr
from typing import Optional, List


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class UserRead(BaseModel):
    id: int
    email: EmailStr
    is_active: bool
    full_name: Optional[str] = None
    roles: List[str] = []
    permissions: List[str] = []


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    sub: Optional[str] = None
    permissions: List[str] = []


class RoleCreate(BaseModel):
    name: str
    description: Optional[str] = None
    permissions: List[str] = []


class RoleRead(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    permissions: List[str] = []


class PermissionRead(BaseModel):
    id: int
    module: str
    action: str
    description: Optional[str] = None
