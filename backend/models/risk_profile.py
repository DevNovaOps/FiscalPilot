"""
Risk Profile model for storing user risk assessment
"""
from datetime import datetime
from ..db import db


class RiskProfile(db.Model):
    """
    Risk Profile model - stores AI-generated risk tolerance assessment
    """
    __tablename__ = "risk_profiles"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    
    # Risk assessment
    risk_score = db.Column(db.Integer, nullable=False)  # 0-100 scale
    risk_level = db.Column(db.String(20), nullable=False)  # Low, Medium, High
    
    # Assessment factors
    income_stability_score = db.Column(db.Float, nullable=True)  # 0-1
    expense_volatility_score = db.Column(db.Float, nullable=True)  # 0-1
    savings_rate = db.Column(db.Float, nullable=True)  # Percentage
    emergency_fund_months = db.Column(db.Float, nullable=True)  # Months of expenses covered
    
    # Behavioral insights
    discretionary_spend_percentage = db.Column(db.Float, nullable=True)
    recurring_obligations_percentage = db.Column(db.Float, nullable=True)
    
    # Explanation (from Explainability Agent)
    explanation = db.Column(db.Text, nullable=True)
    key_factors = db.Column(db.JSON, nullable=True)  # List of factors influencing risk score
    
    # Timestamps
    assessed_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship("User", back_populates="risk_profile")
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "risk_score": self.risk_score,
            "risk_level": self.risk_level,
            "income_stability_score": self.income_stability_score,
            "expense_volatility_score": self.expense_volatility_score,
            "savings_rate": self.savings_rate,
            "emergency_fund_months": self.emergency_fund_months,
            "discretionary_spend_percentage": self.discretionary_spend_percentage,
            "recurring_obligations_percentage": self.recurring_obligations_percentage,
            "explanation": self.explanation,
            "key_factors": self.key_factors,
            "assessed_at": self.assessed_at.isoformat(),
        }
