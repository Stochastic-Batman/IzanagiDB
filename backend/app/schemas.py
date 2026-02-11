from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


# User Schemas
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    user_id: int
    username: str
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True  # Allows conversion from SQLAlchemy models


class UserSearchResult(BaseModel):
    user_id: int
    username: str
    
    class Config:
        from_attributes = True



# Token Schemas
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: int | None = None
    username: str | None = None


# Document Schemas (for later use)
class DocumentCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    content: dict  # JSON content for MongoDB


class DocumentUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    content: dict | None = None


class DocumentShare(BaseModel):
    username: str


class DocumentCommit(BaseModel):
    content: dict  # New version content


class DocumentResponse(BaseModel):
    document_id: int
    title: str
    created_at: datetime
    last_modified_at: datetime
    current_version_number: int | None
    content: dict | None = None  # Include content from MongoDB

    class Config:
        from_attributes = True


class VersionResponse(BaseModel):
    document_id: int
    version_number: int
    modified_by: int | None
    modified_at: datetime
    
    class Config:
        from_attributes = True
