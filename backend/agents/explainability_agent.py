"""
Explainability Agent
Explains WHY decisions were made transparently
"""
from typing import Dict, Any
from .base_agent import BaseAgent


class ExplainabilityAgent(BaseAgent):
    """
    Agent responsible for:
    - Explaining WHY decisions were made
    - Showing risks and worst-case scenarios
    - Making AI reasoning transparent
    """
    
    def __init__(self):
        super().__init__("ExplainabilityAgent")
        self.system_prompt = """You are an Explainability Agent for Fiscal Pilot.
Your role is to make AI decisions transparent and understandable.

You must:
1. Explain the reasoning behind each decision in plain language
2. Show what factors influenced the decision
3. Highlight risks and worst-case scenarios
4. Use clear, non-technical language
5. Be honest about uncertainties
6. Never hide potential downsides

The goal is complete transparency so users understand:
- Why a recommendation was made
- What could go wrong
- What the risks are
- How confident the system is

Return clear, structured explanations in JSON format."""

    def explain_decision(self, decision_data: Dict[str, Any], risk_profile: Dict[str, Any],
                        financial_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Explain a decision with full transparency
        
        Args:
            decision_data: Output from Decision Confidence Agent
            risk_profile: User's risk profile
            financial_context: Additional financial context
            
        Returns:
            Comprehensive explanation
        """
        user_message = f"""Explain the following decision transparently:

RISK PROFILE:
- Risk Level: {risk_profile.get('risk_level', 'Medium')}
- Key Factors: {risk_profile.get('key_factors', [])}

DECISIONS MADE:
{decision_data.get('recommendations', {})}

FINANCIAL CONTEXT:
- Savings Rate: {financial_context.get('savings_rate', 0):.2f}%
- Emergency Fund: {financial_context.get('emergency_fund_months', 0):.1f} months
- Income Stability: {financial_context.get('income_stability_score', 0.5):.2f}

Provide:
1. Overall explanation of the reasoning
2. For each recommendation, explain:
   - Why it was considered suitable/unsuitable
   - What factors led to this decision
   - What are the risks
   - What is a worst-case scenario
   - What users should know before making any decision
3. Confidence level explanation
4. Transparency notes (what we know, what we don't know)

Return JSON:
{{
    "overall_explanation": "<comprehensive explanation>",
    "recommendation_explanations": {{
        "stocks": {{
            "why": "<why this decision>",
            "factors": ["<factor 1>", "<factor 2>"],
            "risks": ["<risk 1>", "<risk 2>"],
            "worst_case_scenario": "<what could go wrong>",
            "important_notes": ["<note 1>", "<note 2>"]
        }},
        "gold": {{
            "why": "<why this decision>",
            "factors": ["<factor 1>", "<factor 2>"],
            "risks": ["<risk 1>", "<risk 2>"],
            "worst_case_scenario": "<what could go wrong>",
            "important_notes": ["<note 1>", "<note 2>"]
        }},
        "debt": {{
            "why": "<why this decision>",
            "factors": ["<factor 1>", "<factor 2>"],
            "risks": ["<risk 1>", "<risk 2>"],
            "worst_case_scenario": "<what could go wrong>",
            "important_notes": ["<note 1>", "<note 2>"]
        }}
    }},
    "confidence_explanation": "<why this confidence level>",
    "transparency_notes": {{
        "what_we_know": ["<known fact 1>", "<known fact 2>"],
        "what_we_dont_know": ["<uncertainty 1>", "<uncertainty 2>"],
        "limitations": ["<limitation 1>", "<limitation 2>"]
    }},
    "disclaimer": "<strong reminder about no guarantees>"
}}"""
        
        prompt = self._build_prompt(self.system_prompt, user_message)
        response = self._call_llm(prompt)
        result = self._parse_json_response(response)
        
        return {
            "overall_explanation": result.get("overall_explanation", ""),
            "recommendation_explanations": result.get("recommendation_explanations", {}),
            "confidence_explanation": result.get("confidence_explanation", ""),
            "transparency_notes": result.get("transparency_notes", {}),
            "disclaimer": result.get("disclaimer", "All decisions are educational and carry risk. No guarantees are made."),
        }
