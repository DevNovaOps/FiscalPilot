"""
AgentAction model for storing autonomous agent decisions
"""
from datetime import datetime
from ..db import db
from sqlalchemy import JSON


class AgentAction(db.Model):
    """
    AgentAction model - stores proactive actions taken by the autonomous financial agent
    
    This is NOT a user request - it's an autonomous agent decision.
    """
    __tablename__ = "agent_actions"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Action details
    action_type = db.Column(db.String(50), nullable=False, index=True)  # WARNING, BUDGET_ADJUSTMENT, SAVING_SUGGESTION
    message = db.Column(db.Text, nullable=False)  # User-facing message
    reasoning = db.Column(db.Text, nullable=False)  # Agent's reasoning (explainable AI)
    
    # Context
    category = db.Column(db.String(100), nullable=True, index=True)  # Category if action is category-specific
    action_metadata = db.Column(JSON, nullable=True)  # Additional structured data (suggested amounts, etc.)
    
    # Status tracking
    resolved = db.Column(db.Boolean, default=False, nullable=False, index=True)
    resolved_at = db.Column(db.DateTime, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    user = db.relationship("User", back_populates="agent_actions")
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "action_type": self.action_type,
            "message": self.message,
            "reasoning": self.reasoning,
            "category": self.category,
            "metadata": self.action_metadata or {},  # Expose as 'metadata' in API for consistency
            "resolved": self.resolved,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "created_at": self.created_at.isoformat(),
        }
