"""
AI Decision model for auditability and explainability
"""
from datetime import datetime
from ..db import db


class AIDecision(db.Model):
    """
    AI Decision model - stores all AI agent decisions for auditability
    Enables explainability and compliance tracking
    """
    __tablename__ = "ai_decisions"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Decision context
    decision_type = db.Column(db.String(100), nullable=False, index=True)  # e.g., "risk_assessment", "investment_suitability"
    agent_name = db.Column(db.String(100), nullable=False)  # Which agent made this decision
    
    # Decision output
    decision_summary = db.Column(db.Text, nullable=False)
    confidence_score = db.Column(db.Float, nullable=True)  # 0-1
    
    # Detailed reasoning
    reasoning = db.Column(db.Text, nullable=True)
    inputs_used = db.Column(db.JSON, nullable=True)  # What data was analyzed
    outputs_generated = db.Column(db.JSON, nullable=True)  # Structured output
    
    # Compliance
    compliance_check_passed = db.Column(db.Boolean, default=True)
    compliance_notes = db.Column(db.Text, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    user = db.relationship("User", back_populates="ai_decisions")
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "decision_type": self.decision_type,
            "agent_name": self.agent_name,
            "decision_summary": self.decision_summary,
            "confidence_score": self.confidence_score,
            "reasoning": self.reasoning,
            "inputs_used": inputs_used if (inputs_used := self.inputs_used) else None,
            "outputs_generated": outputs_generated if (outputs_generated := self.outputs_generated) else None,
            "compliance_check_passed": self.compliance_check_passed,
            "compliance_notes": self.compliance_notes,
            "created_at": self.created_at.isoformat(),
        }
