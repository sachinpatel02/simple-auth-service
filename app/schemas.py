from pydantic import BaseModel, Field, EmailStr, ConfigDict
import uuid
from datetime import datetime

#---------------------------------------------------------------
# Request Schemas : validate requests
#---------------------------------------------------------------

class UserCreate(BaseModel):
    """Schema for creating a new user."""
    email: EmailStr
    password: str= Field(min_length = 8, max_length = 64, 
                         description = "Password must be between 8 and 64 characters long.")

class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str

class RefreshRequest(BaseModel):
    """Schema for refreshing access token."""
    refresh_token: str

#---------------------------------------------------------------
# Response Schemas: validate responses
#---------------------------------------------------------------

class UserResponse(BaseModel):
    """Schema for returning user data. (No password)"""
    id: uuid.UUID
    email: EmailStr
    is_active: bool
    role : str | None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes = True)

class TokenResponse(BaseModel):
    """Schema for returning access and refresh tokens."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    