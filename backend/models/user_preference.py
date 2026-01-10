"""
User Preference model for storing user settings and goals
"""
from datetime import datetime
from ..db import db


class UserPreference(db.Model):
    """
    User Preference model - stores user financial goals and preferences
    """
    __tablename__ = "user_preferences"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    
    # Financial goals
    primary_goal = db.Column(db.String(100), nullable=True)  # retirement, house, emergency_fund, education, etc.
    goal_amount = db.Column(db.Numeric(15, 2), nullable=True)
    goal_timeline_years = db.Column(db.Integer, nullable=True)
    
    # Investment preferences (educational)
    interested_asset_classes = db.Column(db.JSON, nullable=True)  # ["stocks", "gold", "debt"]
    
    # Notification preferences
    email_notifications = db.Column(db.Boolean, default=True)
    insights_frequency = db.Column(db.String(50), default="weekly")  # daily, weekly, monthly
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship("User", back_populates="preferences")
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "primary_goal": self.primary_goal,
            "goal_amount": float(self.goal_amount) if self.goal_amount else None,
            "goal_timeline_years": self.goal_timeline_years,
            "interested_asset_classes": self.interested_asset_classes,
            "email_notifications": self.email_notifications,
            "insights_frequency": self.insights_frequency,
            "created_at": self.created_at.isoformat(),
        }
