"""
User model for authentication and profile management
"""
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from ..db import db


class User(db.Model):
    """
    User model - stores user account information and preferences
    """
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(255), nullable=True)
    
    # Consent tracking
    data_consent = db.Column(db.Boolean, default=False, nullable=False)
    consent_date = db.Column(db.DateTime, nullable=True)
    consent_version = db.Column(db.String(50), nullable=True)
    
    # Preferences
    theme_preference = db.Column(db.String(20), default="dark")  # dark, light
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    transactions = db.relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
    ai_decisions = db.relationship("AIDecision", back_populates="user", cascade="all, delete-orphan")
    preferences = db.relationship("UserPreference", back_populates="user", cascade="all, delete-orphan", uselist=False)
    risk_profile = db.relationship("RiskProfile", back_populates="user", cascade="all, delete-orphan", uselist=False)
    
    def set_password(self, password: str):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        """Verify password"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self, include_sensitive: bool = False):
        """Convert to dictionary for API responses"""
        data = {
            "id": self.id,
            "email": self.email,
            "full_name": self.full_name,
            "theme_preference": self.theme_preference,
            "data_consent": self.data_consent,
            "consent_date": self.consent_date.isoformat() if self.consent_date else None,
            "created_at": self.created_at.isoformat(),
        }
        return data
