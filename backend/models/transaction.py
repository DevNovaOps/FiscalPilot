"""
Transaction model for storing user financial transactions
"""
from datetime import datetime
from decimal import Decimal
from ..db import db


class Transaction(db.Model):
    """
    Transaction model - stores individual financial transactions
    Supports both income and expense transactions
    """
    __tablename__ = "transactions"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Transaction details
    amount = db.Column(db.Numeric(15, 2), nullable=False)  # Positive for income, negative for expense
    description = db.Column(db.Text, nullable=False)
    transaction_date = db.Column(db.Date, nullable=False, index=True)
    transaction_type = db.Column(db.String(50), nullable=False)  # income, expense, transfer
    
    # Categorization (AI-populated)
    category = db.Column(db.String(100), nullable=True, index=True)  # e.g., "Food & Dining", "Salary", "EMI"
    subcategory = db.Column(db.String(100), nullable=True)  # e.g., "Restaurant", "Groceries"
    
    # Additional metadata
    merchant = db.Column(db.String(255), nullable=True)
    payment_method = db.Column(db.String(50), nullable=True)  # credit_card, debit_card, upi, cash, etc.
    
    # Flags (AI-detected)
    is_subscription = db.Column(db.Boolean, default=False)
    is_emi = db.Column(db.Boolean, default=False)
    is_discretionary = db.Column(db.Boolean, default=False)
    is_recurring = db.Column(db.Boolean, default=False)
    
    # Source tracking
    source = db.Column(db.String(50), nullable=False, default="manual")  # manual, csv, mock_aa, plaid
    external_id = db.Column(db.String(255), nullable=True)  # External transaction ID if synced
    transaction_id = db.Column(db.String(255), unique=True, nullable=True, index=True)  # UNIQUE Plaid transaction_id for duplicate prevention
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship("User", back_populates="transactions")
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "amount": float(self.amount),
            "description": self.description,
            "transaction_date": self.transaction_date.isoformat(),
            "transaction_type": self.transaction_type,
            "category": self.category,
            "subcategory": self.subcategory,
            "merchant": self.merchant,
            "payment_method": self.payment_method,
            "is_subscription": self.is_subscription,
            "is_emi": self.is_emi,
            "is_discretionary": self.is_discretionary,
            "is_recurring": self.is_recurring,
            "source": self.source,
            "transaction_id": self.transaction_id,
            "external_id": self.external_id,
            "created_at": self.created_at.isoformat(),
        }
