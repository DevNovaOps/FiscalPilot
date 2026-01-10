"""
PlaidItem model for storing Plaid bank connections
NOTE: This uses Plaid sandbox (demo only), not RBI Account Aggregator
"""
from datetime import datetime
from ..db import db


class PlaidItem(db.Model):
    """
    PlaidItem model - stores Plaid bank account connections
    Stores access_token server-side only for security
    """
    __tablename__ = "plaid_items"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Plaid-specific fields (server-side only, never exposed to frontend)
    access_token = db.Column(db.Text, nullable=False)  # Encrypted/stored securely server-side
    item_id = db.Column(db.String(255), unique=True, nullable=False, index=True)  # Plaid item_id
    
    # Institution info
    institution_name = db.Column(db.String(255), nullable=True)
    institution_id = db.Column(db.String(255), nullable=True)
    
    # Status tracking
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship("User", back_populates="plaid_items")
    
    def to_dict(self, include_sensitive: bool = False):
        """Convert to dictionary for API responses
        
        SECURITY: Never expose access_token to frontend
        """
        data = {
            "id": self.id,
            "user_id": self.user_id,
            "item_id": self.item_id,
            "institution_name": self.institution_name,
            "institution_id": self.institution_id,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
        }
        
        # Only include access_token if explicitly requested (server-side only)
        if include_sensitive:
            data["access_token"] = self.access_token
            
        return data
