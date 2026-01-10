"""
Decision Confidence Agent
Combines behavior + risk + goals to determine suitable options
"""
from typing import Dict, Any, List
from .base_agent import BaseAgent


class DecisionConfidenceAgent(BaseAgent):
    """
    Agent responsible for:
    - Combining behavior analysis + risk profile + user goals
    - Determining which investment options are suitable/unsuitable
    - Providing confidence scores for recommendations
    """
    
    def __init__(self):
        super().__init__("DecisionConfidenceAgent")
        self.system_prompt = """You are a Decision Confidence Agent for Fiscal Pilot.
Your role is to synthesize information from multiple sources and determine suitable financial options.

You receive:
- User's risk profile (Low/Medium/High)
- Financial behavior analysis
- User goals and preferences
- Educational investment information

You must:
1. Match investment options to user's risk profile
2. Consider user's financial situation (savings, stability)
3. Align with user's stated goals
4. Provide confidence scores (0.0-1.0) for each option
5. Clearly mark suitable vs unsuitable options

IMPORTANT:
- This is EDUCATIONAL guidance, not investment advice
- User makes their own decisions
- Always include reasons for suitability/unsuitability
- Never guarantee returns

Return JSON format."""

    def make_decision(self, risk_profile: Dict[str, Any], behavior_data: Dict[str, Any], 
                     user_goals: Dict[str, Any], investment_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make decision about suitable investment options
        
        Args:
            risk_profile: Risk profile assessment
            behavior_data: Financial behavior analysis
            user_goals: User preferences and goals
            investment_info: Educational investment information
            
        Returns:
            Decision with suitable/unsuitable options and confidence scores
        """
        user_message = f"""Based on the following information, determine suitable investment options:

RISK PROFILE:
- Risk Level: {risk_profile.get('risk_level', 'Medium')}
- Risk Score: {risk_profile.get('risk_score', 50)}/100
- Income Stability: {risk_profile.get('income_stability_score', 0.5):.2f}
- Expense Volatility: {risk_profile.get('expense_volatility_score', 0.5):.2f}
- Savings Rate: {risk_profile.get('savings_rate', 0):.2f}%

FINANCIAL BEHAVIOR:
- Average Monthly Income: ₹{behavior_data.get('average_income', 0):.2f}
- Average Monthly Expenses: ₹{behavior_data.get('average_expenses', 0):.2f}
- Emergency Fund: {risk_profile.get('emergency_fund_months', 0):.1f} months
- Recurring Obligations: {risk_profile.get('recurring_obligations_percentage', 0):.2f}%

USER GOALS:
- Primary Goal: {user_goals.get('primary_goal', 'Not specified')}
- Goal Amount: ₹{user_goals.get('goal_amount', 0) or 0:,.2f}
- Timeline: {user_goals.get('goal_timeline_years', 0)} years
- Interested Asset Classes: {user_goals.get('interested_asset_classes', [])}

For each asset class (stocks, gold, debt), determine:
1. Suitability: "suitable", "moderately_suitable", or "unsuitable"
2. Confidence Score: 0.0-1.0
3. Reasoning: Why it's suitable/unsuitable
4. Important Considerations: What user should know

Return JSON:
{{
    "recommendations": {{
        "stocks": {{
            "suitability": "<suitable|moderately_suitable|unsuitable>",
            "confidence_score": <0.0-1.0>,
            "reasoning": "<explanation>",
            "suitable_tiers": ["<low|medium|high>"],
            "considerations": ["<consideration 1>", "<consideration 2>"]
        }},
        "gold": {{
            "suitability": "<suitable|moderately_suitable|unsuitable>",
            "confidence_score": <0.0-1.0>,
            "reasoning": "<explanation>",
            "considerations": ["<consideration 1>", "<consideration 2>"]
        }},
        "debt": {{
            "suitability": "<suitable|moderately_suitable|unsuitable>",
            "confidence_score": <0.0-1.0>,
            "reasoning": "<explanation>",
            "considerations": ["<consideration 1>", "<consideration 2>"]
        }}
    }},
    "overall_confidence": <0.0-1.0>,
    "summary": "<overall recommendation summary>",
    "disclaimer": "<reminder that this is educational>"
}}"""
        
        prompt = self._build_prompt(self.system_prompt, user_message)
        response = self._call_llm(prompt)
        result = self._parse_json_response(response)
        
        return {
            "recommendations": result.get("recommendations", {}),
            "overall_confidence": result.get("overall_confidence", 0.7),
            "summary": result.get("summary", ""),
            "disclaimer": result.get("disclaimer", "This is educational guidance only, not investment advice."),
            "risk_profile_used": risk_profile.get("risk_level"),
        }
