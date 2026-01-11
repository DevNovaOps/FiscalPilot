"""
User Profiling Agent

Analyzes user financial state to create a structured investor profile.
No LLM required - rule-based for explainability.
"""
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from decimal import Decimal
from ...models import Transaction, User, RiskProfile, UserPreference


class ProfilerAgent:
    """
    User Profiling Agent
    
    Analyzes:
    - Income stability
    - Monthly surplus
    - Age (if available)
    - Risk tolerance (from RiskProfile)
    - Goals (from UserPreference)
    - Spending patterns
    
    Outputs a structured investor profile.
    """
    
    def __init__(self):
        self.agent_name = "ProfilerAgent"
    
    def analyze_user(self, user_id: int) -> Dict[str, Any]:
        """
        Analyze user financial state and create investor profile
        
        Returns:
            Dict with structured investor profile
        """
        # Get user data
        user = User.query.get(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        # Get transactions (last 90 days for stability analysis)
        ninety_days_ago = datetime.utcnow().date() - timedelta(days=90)
        transactions = Transaction.query.filter(
            Transaction.user_id == user_id,
            Transaction.transaction_date >= ninety_days_ago
        ).all()
        
        # Calculate monthly income and expenses
        monthly_data = self._calculate_monthly_financials(transactions)
        
        # Get risk profile
        risk_profile = RiskProfile.query.filter_by(user_id=user_id).first()
        
        # Get user preferences
        user_prefs = UserPreference.query.filter_by(user_id=user_id).first()
        
        # Calculate income stability
        income_stability = self._calculate_income_stability(monthly_data)
        
        # Calculate monthly surplus
        avg_income = monthly_data['avg_income']
        avg_expenses = monthly_data['avg_expenses']
        monthly_surplus = avg_income - avg_expenses
        surplus_percentage = (monthly_surplus / avg_income * 100) if avg_income > 0 else 0
        
        # Determine risk tolerance
        risk_tolerance = "Medium"  # Default
        if risk_profile:
            risk_tolerance = risk_profile.risk_level
        elif monthly_surplus > avg_income * 0.3:
            risk_tolerance = "High"
        elif monthly_surplus < avg_income * 0.1:
            risk_tolerance = "Low"
        
        # Determine investor type
        investor_type = self._determine_investor_type(
            income_stability, monthly_surplus, risk_tolerance, user_prefs
        )
        
        # Extract goals
        goals = self._extract_goals(user_prefs)
        
        profile = {
            "agent": self.agent_name,
            "confidence": 0.85,
            "investor_type": investor_type,
            "risk_tolerance": risk_tolerance,
            "income_stability": income_stability,
            "monthly_income": float(avg_income),
            "monthly_expenses": float(avg_expenses),
            "monthly_surplus": float(monthly_surplus),
            "surplus_percentage": round(surplus_percentage, 2),
            "goals": goals,
            "emergency_fund_months": monthly_data.get('emergency_fund_months', 0),
            "expense_volatility": monthly_data.get('expense_volatility', 0),
        }
        
        return profile
    
    def _calculate_monthly_financials(self, transactions: list) -> Dict[str, Any]:
        """Calculate monthly income, expenses, and patterns"""
        monthly_income = {}
        monthly_expenses = {}
        
        for tx in transactions:
            month_key = tx.transaction_date.strftime("%Y-%m")
            
            if tx.transaction_type == 'income' and tx.amount > 0:
                monthly_income[month_key] = monthly_income.get(month_key, 0) + float(tx.amount)
            elif tx.transaction_type == 'expense' and tx.amount < 0:
                monthly_expenses[month_key] = monthly_expenses.get(month_key, 0) + abs(float(tx.amount))
        
        # Calculate averages
        avg_income = sum(monthly_income.values()) / len(monthly_income) if monthly_income else 0
        avg_expenses = sum(monthly_expenses.values()) / len(monthly_expenses) if monthly_expenses else 0
        
        # Calculate expense volatility (coefficient of variation)
        expense_values = list(monthly_expenses.values())
        if len(expense_values) > 1:
            mean_exp = sum(expense_values) / len(expense_values)
            variance = sum((x - mean_exp) ** 2 for x in expense_values) / len(expense_values)
            std_dev = variance ** 0.5
            expense_volatility = (std_dev / mean_exp) if mean_exp > 0 else 0
        else:
            expense_volatility = 0
        
        # Estimate emergency fund (assume 3 months expenses if no data)
        emergency_fund_months = 3.0  # Default assumption
        
        return {
            'avg_income': avg_income,
            'avg_expenses': avg_expenses,
            'monthly_income': monthly_income,
            'monthly_expenses': monthly_expenses,
            'expense_volatility': expense_volatility,
            'emergency_fund_months': emergency_fund_months,
        }
    
    def _calculate_income_stability(self, monthly_data: Dict) -> str:
        """Calculate income stability score"""
        monthly_income = monthly_data['monthly_income']
        
        if len(monthly_income) < 2:
            return "unknown"
        
        income_values = list(monthly_income.values())
        mean_income = sum(income_values) / len(income_values)
        
        # Calculate coefficient of variation
        variance = sum((x - mean_income) ** 2 for x in income_values) / len(income_values)
        std_dev = variance ** 0.5
        cv = (std_dev / mean_income) if mean_income > 0 else 0
        
        if cv < 0.1:
            return "very_stable"
        elif cv < 0.2:
            return "stable"
        elif cv < 0.3:
            return "moderate"
        else:
            return "volatile"
    
    def _determine_investor_type(
        self, 
        income_stability: str, 
        monthly_surplus: float,
        risk_tolerance: str,
        user_prefs: Optional[Any]
    ) -> str:
        """Determine investor type based on profile"""
        if income_stability in ["very_stable", "stable"] and monthly_surplus > 0:
            if risk_tolerance == "High":
                return "Growth-Oriented Investor"
            elif risk_tolerance == "Low":
                return "Conservative Investor"
            else:
                return "Balanced Investor"
        elif income_stability == "volatile":
            return "Cautious Investor"
        elif monthly_surplus <= 0:
            return "Rebuilding Investor"
        else:
            return "Emerging Investor"
    
    def _extract_goals(self, user_prefs: Optional[Any]) -> Dict[str, Any]:
        """Extract goals from user preferences"""
        if not user_prefs:
            return {
                "has_goals": False,
                "primary_goal": None,
                "goal_amount": None,
                "goal_timeline_years": None,
            }
        
        return {
            "has_goals": bool(user_prefs.primary_goal),
            "primary_goal": user_prefs.primary_goal,
            "goal_amount": float(user_prefs.goal_amount) if user_prefs.goal_amount else None,
            "goal_timeline_years": user_prefs.goal_timeline_years,
        }