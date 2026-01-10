"""
User schemas for validation
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class UserCreate(BaseModel):
    """Schema for user registration"""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    full_name: Optional[str] = Field(None, max_length=255)
    data_consent: bool = Field(..., description="User must consent to data usage")


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Schema for user API response"""
    id: int
    email: str
    full_name: Optional[str] = None
    theme_preference: str
    data_consent: bool
    consent_date: Optional[str] = None
    created_at: str
