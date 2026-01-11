"""
Investment Recommendation model for storing multi-agent investment advice
"""
from datetime import datetime
from ..db import db


class InvestmentRecommendation(db.Model):
    """
    Investment Recommendation model - stores investment advice from multi-agent system
    
    This model stores the final recommendation after all agents have
    analyzed the user's profile and reached consensus.
    """
    __tablename__ = "investment_recommendations"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Selected investment path(s)
    selected_path = db.Column(db.String(100), nullable=False)  # e.g., "Balanced Path", "Conservative Path"
    selected_paths = db.Column(db.JSON, nullable=True)  # Array of paths if multiple
    
    # Investor profile (from ProfilerAgent)
    investor_type = db.Column(db.String(100), nullable=True)  # e.g., "Stable Income Growth Investor"
    risk_tolerance = db.Column(db.String(50), nullable=True)  # Low, Medium, High
    
    # Detected intent (from IntentAgent)
    primary_intent = db.Column(db.String(100), nullable=True)  # wealth_growth, passive_income, capital_protection, learning
    
    # Agent outputs (JSON)
    profiler_output = db.Column(db.JSON, nullable=True)  # ProfilerAgent output
    intent_output = db.Column(db.JSON, nullable=True)  # IntentAgent output
    router_output = db.Column(db.JSON, nullable=True)  # RouterAgent output
    equity_output = db.Column(db.JSON, nullable=True)  # EquityAgent output (if applicable)
    etf_output = db.Column(db.JSON, nullable=True)  # ETFAgent output (if applicable)
    risk_output = db.Column(db.JSON, nullable=True)  # RiskAgent output
    
    # Final recommendations (structured JSON)
    recommendations = db.Column(db.JSON, nullable=False)  # Final structured recommendations
    
    # Reasoning and explanation (from ConsensusAgent)
    reasoning = db.Column(db.Text, nullable=False)  # Why this path was chosen
    agent_reasoning = db.Column(db.JSON, nullable=True)  # Individual agent reasoning summaries
    
    # Safety flags (from RiskAgent)
    safety_override = db.Column(db.Boolean, default=False)  # True if risk agent blocked a path
    safety_reason = db.Column(db.Text, nullable=True)  # Reason for safety override
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship("User", backref="investment_recommendations")
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "selected_path": self.selected_path,
            "selected_paths": self.selected_paths,
            "investor_type": self.investor_type,
            "risk_tolerance": self.risk_tolerance,
            "primary_intent": self.primary_intent,
            "profiler_output": self.profiler_output,
            "intent_output": self.intent_output,
            "router_output": self.router_output,
            "equity_output": self.equity_output,
            "etf_output": self.etf_output,
            "risk_output": self.risk_output,
            "recommendations": self.recommendations,
            "reasoning": self.reasoning,
            "agent_reasoning": self.agent_reasoning,
            "safety_override": self.safety_override,
            "safety_reason": self.safety_reason,
            "created_at": self.created_at.isoformat(),
        }