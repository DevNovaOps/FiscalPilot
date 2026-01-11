"""
LangChain tools for agents to interact with data
"""
from typing import List, Dict, Any, Optional
from decimal import Decimal
from datetime import datetime, timedelta
from langchain_core.tools import tool
from ..db import db
from ..models.transaction import Transaction
from ..models.user_preference import UserPreference


class TransactionTools:
    """
    Tools for Transaction Intelligence Agent
    Provides functions to query and analyze transactions
    """
    
    @staticmethod
    # @tool
    def get_user_transactions(user_id: int, days: int = 90) -> List[Dict[str, Any]]:
        """
        Get user transactions for the last N days
        
        Args:
            user_id: User ID
            days: Number of days to look back (default: 90)
            
        Returns:
            List of transaction dictionaries
        """
        cutoff_date = datetime.utcnow().date() - timedelta(days=days)
        transactions = Transaction.query.filter(
            Transaction.user_id == user_id,
            Transaction.transaction_date >= cutoff_date
        ).order_by(Transaction.transaction_date.desc()).all()
        
        return [t.to_dict() for t in transactions]
    
    @staticmethod
    # @tool
    def get_transactions_by_category(user_id: int, category: str) -> List[Dict[str, Any]]:
        """
        Get transactions by category
        
        Args:
            user_id: User ID
            category: Category name
            
        Returns:
            List of transactions in that category
        """
        transactions = Transaction.query.filter(
            Transaction.user_id == user_id,
            Transaction.category == category
        ).all()
        
        return [t.to_dict() for t in transactions]
    
    @staticmethod
    # @tool
    def get_monthly_summary(user_id: int, months: int = 6) -> Dict[str, Any]:
        """
        Get monthly income and expense summary
        
        Args:
            user_id: User ID
            months: Number of months to analyze
            
        Returns:
            Dictionary with monthly summaries
        """
        now = datetime.utcnow().date()
        summary = {}
        
        for i in range(months):
            month_start = (now.replace(day=1) - timedelta(days=30 * i)).replace(day=1)
            if i == 0:
                month_end = now
            else:
                month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            
            transactions = Transaction.query.filter(
                Transaction.user_id == user_id,
                Transaction.transaction_date >= month_start,
                Transaction.transaction_date <= month_end
            ).all()
            
            income = sum(float(t.amount) for t in transactions if t.transaction_type == "income" and float(t.amount) > 0)
            expenses = sum(abs(float(t.amount)) for t in transactions if t.transaction_type == "expense" and float(t.amount) < 0)
            
            month_key = month_start.strftime("%Y-%m")
            summary[month_key] = {
                "income": income,
                "expenses": expenses,
                "net": income - expenses,
                "transaction_count": len(transactions),
            }
        
        return summary


class FinancialAnalysisTools:
    """
    Tools for Financial Behavior Agent
    Provides functions to analyze financial patterns
    """
    
    @staticmethod
    # @tool
    def calculate_savings_rate(user_id: int, months: int = 3) -> Dict[str, Any]:
        """
        Calculate average savings rate over last N months
        
        Args:
            user_id: User ID
            months: Number of months to analyze
            
        Returns:
            Dictionary with savings rate and related metrics
        """
        now = datetime.utcnow().date()
        total_income = 0
        total_expenses = 0
        
        for i in range(months):
            month_start = (now.replace(day=1) - timedelta(days=30 * i)).replace(day=1)
            if i == 0:
                month_end = now
            else:
                month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            
            transactions = Transaction.query.filter(
                Transaction.user_id == user_id,
                Transaction.transaction_date >= month_start,
                Transaction.transaction_date <= month_end
            ).all()
            
            month_income = sum(float(t.amount) for t in transactions if t.transaction_type == "income" and float(t.amount) > 0)
            month_expenses = sum(abs(float(t.amount)) for t in transactions if t.transaction_type == "expense" and float(t.amount) < 0)
            
            total_income += month_income
            total_expenses += month_expenses
        
        avg_savings = total_income - total_expenses
        savings_rate = (avg_savings / total_income * 100) if total_income > 0 else 0
        
        return {
            "savings_rate_percentage": savings_rate,
            "average_income": total_income / months if months > 0 else 0,
            "average_expenses": total_expenses / months if months > 0 else 0,
            "average_savings": avg_savings / months if months > 0 else 0,
            "months_analyzed": months,
        }
    
    @staticmethod
    # @tool
    def detect_recurring_expenses(user_id: int) -> Dict[str, Any]:
        """
        Detect recurring expenses (subscriptions, EMIs, etc.)
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with recurring expense analysis
        """
        transactions = Transaction.query.filter(
            Transaction.user_id == user_id
        ).order_by(Transaction.transaction_date.desc()).limit(500).all()
        
        subscriptions = [t for t in transactions if t.is_subscription]
        emis = [t for t in transactions if t.is_emi]
        recurring = [t for t in transactions if t.is_recurring]
        
        return {
            "subscription_count": len(subscriptions),
            "subscription_total": sum(abs(float(t.amount)) for t in subscriptions),
            "emi_count": len(emis),
            "emi_total": sum(abs(float(t.amount)) for t in emis),
            "recurring_count": len(recurring),
            "recurring_total": sum(abs(float(t.amount)) for t in recurring),
        }
    
    @staticmethod
    # @tool
    def get_user_preferences(user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get user financial preferences and goals
        
        Args:
            user_id: User ID
            
        Returns:
            User preferences dictionary or None
        """
        prefs = UserPreference.query.filter_by(user_id=user_id).first()
        return prefs.to_dict() if prefs else None
