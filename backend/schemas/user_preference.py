"""
User Preference schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List


class UserPreferenceCreate(BaseModel):
    """Schema for creating/updating user preferences"""
    primary_goal: Optional[str] = Field(None, max_length=100)
    goal_amount: Optional[float] = Field(None, ge=0)
    goal_timeline_years: Optional[int] = Field(None, ge=0, le=100)
    interested_asset_classes: Optional[List[str]] = Field(None)
    email_notifications: Optional[bool] = None
    insights_frequency: Optional[str] = Field(None, pattern="^(daily|weekly|monthly)$")


class UserPreferenceResponse(BaseModel):
    """Schema for user preference API response"""
    id: int
    user_id: int
    primary_goal: Optional[str] = None
    goal_amount: Optional[float] = None
    goal_timeline_years: Optional[int] = None
    interested_asset_classes: Optional[List[str]] = None
    email_notifications: bool
    insights_frequency: str
    created_at: str
