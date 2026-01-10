"""
Transaction schemas for validation
"""
from pydantic import BaseModel, Field, field_validator
from datetime import date
from decimal import Decimal
from typing import Optional


class TransactionCreate(BaseModel):
    """Schema for creating a new transaction"""
    amount: float = Field(..., description="Transaction amount (positive for income, negative for expense)")
    description: str = Field(..., min_length=1, max_length=1000)
    transaction_date: date = Field(..., description="Date of transaction")
    transaction_type: str = Field(..., pattern="^(income|expense|transfer)$")
    category: Optional[str] = Field(None, max_length=100)
    subcategory: Optional[str] = Field(None, max_length=100)
    merchant: Optional[str] = Field(None, max_length=255)
    payment_method: Optional[str] = Field(None, max_length=50)
    source: str = Field(default="manual", pattern="^(manual|csv|mock_aa|plaid)$")
    external_id: Optional[str] = Field(None, max_length=255)
    
    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v):
        if v == 0:
            raise ValueError("Amount cannot be zero")
        return v


class TransactionResponse(BaseModel):
    """Schema for transaction API response"""
    id: int
    user_id: int
    amount: float
    description: str
    transaction_date: str
    transaction_type: str
    category: Optional[str] = None
    subcategory: Optional[str] = None
    merchant: Optional[str] = None
    payment_method: Optional[str] = None
    is_subscription: bool
    is_emi: bool
    is_discretionary: bool
    is_recurring: bool
    source: str
    created_at: str
