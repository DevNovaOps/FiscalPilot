"""
Investment Knowledge Agent
Provides educational content about investment options
"""
from typing import Dict, Any, List
from .base_agent import BaseAgent


class InvestmentKnowledgeAgent(BaseAgent):
    """
    Agent responsible for:
    - Providing educational knowledge about stocks, gold, debt
    - Explaining risk tiers
    - NO predictions, only ranges and explanations
    """
    
    def __init__(self):
        super().__init__("InvestmentKnowledgeAgent")
        self.system_prompt = """You are an Investment Knowledge Agent for Fiscal Pilot.
Your role is to provide EDUCATIONAL information about investment options.

CRITICAL RULES:
1. NEVER predict specific returns or guarantee outcomes
2. Provide RISK-BASED education only
3. Explain historical ranges, not future promises
4. Always include disclaimers about risk
5. This is NOT investment advice

Asset Classes:

STOCKS:
- Low Risk (Blue-chip, large-cap): Historical range varies, high volatility possible
- Medium Risk (Mid-cap): Higher volatility than large-cap
- High Risk (Small-cap, sector-specific): Very high volatility, potential for losses
- Explain: Market-linked, can go up or down, past performance ≠ future results

GOLD:
- Physical Gold: Storage costs, liquidity considerations
- Gold ETFs/Mutual Funds: Easier liquidity, management fees
- Historical: Hedge against inflation, but price can fluctuate
- Explain: Not guaranteed to always increase, market-dependent

DEBT/SAFE ASSETS:
- Fixed Deposits: Fixed returns (current rates vary), low risk
- Government Bonds: Very low risk, predictable income
- Debt Mutual Funds: Low to moderate risk, subject to interest rate changes
- Explain: Lower returns but higher stability

Always emphasize: All investments carry risk. Past performance does not guarantee future results."""

    def get_investment_education(self, risk_level: str, asset_classes: List[str] = None) -> Dict[str, Any]:
        """
        Get educational content about investment options
        
        Args:
            risk_level: User's risk level (Low, Medium, High)
            asset_classes: List of asset classes user is interested in
            
        Returns:
            Educational content about investments
        """
        if asset_classes is None:
            asset_classes = ["stocks", "gold", "debt"]
        
        user_message = f"""Provide educational information about investments suitable for a {risk_level} risk profile.

User is interested in: {', '.join(asset_classes)}

For each asset class, provide:
1. General description
2. Risk characteristics
3. Historical context (ranges, not predictions)
4. Suitability for {risk_level} risk profile
5. Important considerations and risks
6. Disclaimer reminders

Return JSON:
{{
    "asset_classes": {{
        "stocks": {{
            "description": "<educational description>",
            "risk_tiers": {{
                "low": "<info about low-risk stocks>",
                "medium": "<info about medium-risk stocks>",
                "high": "<info about high-risk stocks>"
            }},
            "suitability_for_{risk_level.lower()}": "<why suitable or not>",
            "key_risks": ["<risk 1>", "<risk 2>"],
            "historical_context": "<educational note, no predictions>"
        }},
        "gold": {{
            "description": "<educational description>",
            "forms": {{
                "physical": "<info>",
                "etf": "<info>",
                "mutual_funds": "<info>"
            }},
            "suitability_for_{risk_level.lower()}": "<why suitable or not>",
            "key_risks": ["<risk 1>", "<risk 2>"],
            "historical_context": "<educational note>"
        }},
        "debt": {{
            "description": "<educational description>",
            "options": {{
                "fixed_deposits": "<info>",
                "government_bonds": "<info>",
                "debt_mutual_funds": "<info>"
            }},
            "suitability_for_{risk_level.lower()}": "<why suitable or not>",
            "key_risks": ["<risk 1>", "<risk 2>"],
            "historical_context": "<educational note>"
        }}
    }},
    "disclaimer": "<strong disclaimer about no guarantees>"
}}"""
        
        prompt = self._build_prompt(self.system_prompt, user_message)
        response = self._call_llm(prompt)
        result = self._parse_json_response(response)
        
        return {
            "asset_classes": result.get("asset_classes", {}),
            "disclaimer": result.get("disclaimer", "All investments carry risk. Past performance does not guarantee future results."),
            "risk_level": risk_level,
        }
