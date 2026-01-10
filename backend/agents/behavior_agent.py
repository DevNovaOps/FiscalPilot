"""
Financial Behavior Agent
Analyzes spending patterns and calculates risk tolerance
"""
from typing import Dict, Any
from .base_agent import BaseAgent
from .tools import FinancialAnalysisTools


class FinancialBehaviorAgent(BaseAgent):
    """
    Agent responsible for:
    - Analyzing income stability
    - Measuring expense volatility
    - Calculating risk tolerance score (Low/Medium/High)
    """
    
    def __init__(self):
        super().__init__("FinancialBehaviorAgent")
        self.system_prompt = """You are a Financial Behavior Agent for Fiscal Pilot.
Your role is to analyze user financial behavior and assess risk tolerance.

Risk factors to consider:
1. Income Stability: Regular vs irregular income
2. Expense Volatility: Consistent vs fluctuating expenses
3. Savings Rate: Percentage of income saved
4. Emergency Fund: Months of expenses covered
5. Recurring Obligations: % of income going to EMIs/subscriptions
6. Discretionary Spending: % of income for non-essential items

Risk Levels:
- Low (0-35): Stable income, low expenses, high savings, minimal debt
- Medium (36-65): Moderate stability, some volatility, decent savings
- High (66-100): Irregular income, high volatility, low savings, high obligations

IMPORTANT: This is an assessment, not investment advice.
Return JSON format."""

    def assess_risk_profile(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess user's financial risk profile
        
        Args:
            financial_data: Dictionary with savings_rate, income_stability, expense_volatility, etc.
            
        Returns:
            Risk profile assessment
        """
        user_message = f"""Assess the financial risk profile based on this data:

Savings Rate: {financial_data.get('savings_rate_percentage', 0):.2f}%
Average Monthly Income: ₹{financial_data.get('average_income', 0):.2f}
Average Monthly Expenses: ₹{financial_data.get('average_expenses', 0):.2f}
Recurring Obligations: ₹{financial_data.get('recurring_total', 0):.2f}
Discretionary Spending: {financial_data.get('discretionary_percentage', 0):.2f}%

Monthly Summary:
{financial_data.get('monthly_summary', {})}

Calculate:
1. risk_score (0-100 integer)
2. risk_level ("Low", "Medium", or "High")
3. income_stability_score (0.0-1.0)
4. expense_volatility_score (0.0-1.0, higher = more volatile)
5. Key factors influencing the score

Return JSON:
{{
    "risk_score": <0-100>,
    "risk_level": "<Low|Medium|High>",
    "income_stability_score": <0.0-1.0>,
    "expense_volatility_score": <0.0-1.0>,
    "savings_rate": <percentage>,
    "emergency_fund_months": <calculated months>,
    "discretionary_spend_percentage": <percentage>,
    "recurring_obligations_percentage": <percentage>,
    "key_factors": [
        {{
            "factor": "<name>",
            "impact": "<positive|negative|neutral>",
            "description": "<explanation>"
        }}
    ],
    "reasoning": "<overall assessment reasoning>"
}}"""
        
        prompt = self._build_prompt(self.system_prompt, user_message)
        response = self._call_llm(prompt)
        result = self._parse_json_response(response)
        
        # Ensure risk_score is integer and within bounds
        risk_score = result.get("risk_score", 50)
        if isinstance(risk_score, float):
            risk_score = int(round(risk_score))
        risk_score = max(0, min(100, risk_score))
        
        # Map score to level if not provided
        if "risk_level" not in result:
            if risk_score <= 35:
                risk_level = "Low"
            elif risk_score <= 65:
                risk_level = "Medium"
            else:
                risk_level = "High"
        else:
            risk_level = result.get("risk_level", "Medium")
        
        return {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "income_stability_score": result.get("income_stability_score", 0.5),
            "expense_volatility_score": result.get("expense_volatility_score", 0.5),
            "savings_rate": result.get("savings_rate", financial_data.get("savings_rate_percentage", 0)),
            "emergency_fund_months": result.get("emergency_fund_months", 0),
            "discretionary_spend_percentage": result.get("discretionary_spend_percentage", 0),
            "recurring_obligations_percentage": result.get("recurring_obligations_percentage", 0),
            "key_factors": result.get("key_factors", []),
            "reasoning": result.get("reasoning", ""),
        }
