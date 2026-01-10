"""
AI Decision schemas
"""
from pydantic import BaseModel
from typing import Optional, Dict, Any


class AIDecisionResponse(BaseModel):
    """Schema for AI decision API response"""
    id: int
    user_id: int
    decision_type: str
    agent_name: str
    decision_summary: str
    confidence_score: Optional[float] = None
    reasoning: Optional[str] = None
    inputs_used: Optional[Dict[str, Any]] = None
    outputs_generated: Optional[Dict[str, Any]] = None
    compliance_check_passed: bool
    compliance_notes: Optional[str] = None
    created_at: str
