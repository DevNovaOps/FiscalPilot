"""
Transaction Intelligence Agent
Categorizes expenses and detects patterns
"""
from typing import Dict, Any, List
from .base_agent import BaseAgent
from .tools import TransactionTools


class TransactionIntelligenceAgent(BaseAgent):
    """
    Agent responsible for:
    - Categorizing transactions
    - Detecting EMI, subscriptions, discretionary spend
    - Identifying patterns in spending
    """
    
    def __init__(self):
        super().__init__("TransactionIntelligenceAgent")
        self.system_prompt = """You are a Transaction Intelligence Agent for Fiscal Pilot.
Your role is to analyze financial transactions and categorize them accurately.

Categories include:
- Food & Dining (Restaurants, Groceries, Food Delivery)
- Transportation (Fuel, Public Transport, Rideshare, Parking)
- Shopping (Clothing, Electronics, General Retail)
- Bills & Utilities (Electricity, Water, Internet, Phone)
- Entertainment (Movies, Streaming, Games, Events)
- Healthcare (Doctor, Pharmacy, Insurance)
- Education (Tuition, Books, Courses)
- Personal Care (Salon, Gym, Wellness)
- Travel (Hotels, Flights, Vacation)
- EMI (Loan repayments, Installments)
- Subscriptions (Netflix, Spotify, Software)
- Salary/Income (Salary, Freelance, Investment Returns)
- Other

Flags to detect:
- is_subscription: Recurring subscription payments
- is_emi: Loan or installment payments
- is_discretionary: Non-essential spending
- is_recurring: Any recurring transaction pattern

Be precise and consistent. Return JSON format."""

    def analyze_transactions(self, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze transactions and categorize them
        
        Args:
            transactions: List of transaction dictionaries
            
        Returns:
            Analysis result with categories and flags
        """
        if not transactions:
            return {
                "categorized_transactions": [],
                "category_summary": {},
                "total_transactions": 0,
            }
        
        # Build context for LLM
        transaction_summary = "\n".join([
            f"{t.get('description', 'N/A')} | {t.get('amount', 0)} | {t.get('transaction_date', 'N/A')}"
            for t in transactions[:50]  # Limit to avoid token limits
        ])
        
        user_message = f"""Analyze these transactions and categorize them:

{transaction_summary}

For each transaction, provide:
1. category (from the list above)
2. subcategory (more specific)
3. is_subscription (true/false)
4. is_emi (true/false)
5. is_discretionary (true/false)
6. is_recurring (true/false)

Return JSON in this format:
{{
    "analysis": [
        {{
            "transaction_id": <id>,
            "category": "<category>",
            "subcategory": "<subcategory>",
            "is_subscription": <bool>,
            "is_emi": <bool>,
            "is_discretionary": <bool>,
            "is_recurring": <bool>,
            "reasoning": "<brief explanation>"
        }}
    ],
    "category_summary": {{
        "<category>": {{
            "count": <number>,
            "total_amount": <number>
        }}
    }}
}}"""
        
        prompt = self._build_prompt(self.system_prompt, user_message)
        response = self._call_llm(prompt)
        result = self._parse_json_response(response)
        
        # Merge with original transactions
        categorized = []
        for i, tx in enumerate(transactions[:50]):
            analysis = result.get("analysis", [])
            if i < len(analysis):
                tx_analysis = analysis[i]
                tx.update({
                    "category": tx_analysis.get("category", tx.get("category")),
                    "subcategory": tx_analysis.get("subcategory"),
                    "is_subscription": tx_analysis.get("is_subscription", False),
                    "is_emi": tx_analysis.get("is_emi", False),
                    "is_discretionary": tx_analysis.get("is_discretionary", False),
                    "is_recurring": tx_analysis.get("is_recurring", False),
                })
            categorized.append(tx)
        
        return {
            "categorized_transactions": categorized,
            "category_summary": result.get("category_summary", {}),
            "total_transactions": len(transactions),
            "raw_analysis": result,
        }
