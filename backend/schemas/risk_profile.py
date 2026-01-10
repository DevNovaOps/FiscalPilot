"""
Risk Profile schemas
"""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class RiskProfileResponse(BaseModel):
    """Schema for risk profile API response"""
    id: int
    user_id: int
    risk_score: int
    risk_level: str
    income_stability_score: Optional[float] = None
    expense_volatility_score: Optional[float] = None
    savings_rate: Optional[float] = None
    emergency_fund_months: Optional[float] = None
    discretionary_spend_percentage: Optional[float] = None
    recurring_obligations_percentage: Optional[float] = None
    explanation: Optional[str] = None
    key_factors: Optional[List[Dict[str, Any]]] = None
    assessed_at: str
