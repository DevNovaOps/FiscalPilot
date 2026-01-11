"""
Mutual Fund / ETF Agent

Suggests mutual fund and ETF strategies with SIP recommendations.
Educational and advisory tone.
"""
from typing import Dict, Any


class ETFAgent:
    """
    Mutual Fund / ETF Agent
    
    Suggests:
    - SIP strategy
    - Index ETFs
    - Asset allocation ideas
    - Educational guidance
    """
    
    def __init__(self):
        self.agent_name = "ETFAgent"
    
    def analyze_etf(
        self, 
        profiler_output: Dict[str, Any],
        intent_output: Dict[str, Any],
        router_output: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze ETF/Mutual Fund strategy
        
        Args:
            profiler_output: Output from ProfilerAgent
            intent_output: Output from IntentAgent
            router_output: Output from RouterAgent
            
        Returns:
            Dict with ETF/Mutual Fund suggestions
        """
        risk_tolerance = profiler_output.get("risk_tolerance", "Medium")
        monthly_surplus = profiler_output.get("monthly_surplus", 0)
        primary_intent = intent_output.get("primary_intent", "wealth_growth")
        selected_paths = router_output.get("selected_paths", [])
        is_beginner = "beginner" in selected_paths
        
        # Determine ETF strategy
        strategy = self._determine_strategy(risk_tolerance, primary_intent, is_beginner)
        
        # Generate suggestions
        suggestions = self._generate_suggestions(strategy, monthly_surplus, risk_tolerance)
        
        # Calculate SIP recommendation
        sip_amount = self._calculate_sip_amount(monthly_surplus, risk_tolerance)
        
        # Calculate confidence
        confidence = 0.80 if monthly_surplus > 5000 else 0.70
        
        return {
            "agent": self.agent_name,
            "confidence": confidence,
            "strategy": strategy,
            "suggestions": suggestions,
            "sip_recommendation": sip_amount,
            "risk_level": risk_tolerance.lower(),
            "educational_note": "SIP (Systematic Investment Plan) helps in disciplined investing and reduces impact of market timing. All investments carry risk.",
        }
    
    def _determine_strategy(
        self, 
        risk_tolerance: str, 
        primary_intent: str,
        is_beginner: bool
    ) -> str:
        """Determine ETF/Mutual Fund strategy"""
        if is_beginner:
            return "beginner_sip"
        elif risk_tolerance == "Low":
            return "conservative_funds"
        elif risk_tolerance == "High":
            return "growth_funds"
        else:
            return "balanced_funds"
    
    def _generate_suggestions(
        self, 
        strategy: str, 
        monthly_surplus: float,
        risk_tolerance: str
    ) -> Dict[str, Any]:
        """Generate ETF/Mutual Fund suggestions"""
        suggestions = {
            "fund_categories": [],
            "allocation_suggestion": None,
            "investment_approach": "",
            "educational_points": [],
        }
        
        if strategy == "beginner_sip":
            suggestions["fund_categories"] = [
                "Large-cap index funds or ETFs",
                "Balanced funds (equity + debt mix)",
                "Conservative hybrid funds"
            ]
            suggestions["allocation_suggestion"] = "Start with 30-40% of monthly surplus in SIPs"
            suggestions["investment_approach"] = "Beginner-friendly approach with focus on learning and steady growth"
            suggestions["educational_points"] = [
                "SIP allows investing small amounts regularly",
                "Index funds are simple and cost-effective",
                "Balanced funds provide automatic diversification"
            ]
        elif strategy == "conservative_funds":
            suggestions["fund_categories"] = [
                "Large-cap index ETFs",
                "Debt funds for stability",
                "Balanced funds with debt tilt"
            ]
            suggestions["allocation_suggestion"] = "Consider allocating 50-60% of investment surplus to funds"
            suggestions["investment_approach"] = "Conservative approach focusing on capital preservation with growth"
            suggestions["educational_points"] = [
                "Large-cap funds offer stability with market returns",
                "Debt funds provide income generation with lower risk",
                "Balanced allocation helps manage volatility"
            ]
        elif strategy == "growth_funds":
            suggestions["fund_categories"] = [
                "Broad-market index ETFs",
                "Mid-cap and small-cap index funds",
                "Sector-specific ETFs (with caution)"
            ]
            suggestions["allocation_suggestion"] = "Consider allocating 60-70% of investment surplus to funds"
            suggestions["investment_approach"] = "Growth-oriented approach with focus on long-term wealth accumulation"
            suggestions["educational_points"] = [
                "Index ETFs provide broad market exposure at low cost",
                "Mid-cap and small-cap funds offer higher growth potential with higher risk",
                "Diversification across market caps balances risk and return"
            ]
        else:  # balanced_funds
            suggestions["fund_categories"] = [
                "Large-cap and mid-cap index funds",
                "Balanced funds",
                "Multi-cap index ETFs"
            ]
            suggestions["allocation_suggestion"] = "Consider allocating 50-60% of investment surplus to funds"
            suggestions["investment_approach"] = "Balanced approach with diversified fund portfolio"
            suggestions["educational_points"] = [
                "Diversification across market caps and asset classes reduces risk",
                "Balanced funds automatically adjust allocation",
                "Index funds eliminate fund manager risk and reduce costs"
            ]
        
        return suggestions
    
    def _calculate_sip_amount(self, monthly_surplus: float, risk_tolerance: str) -> Dict[str, Any]:
        """Calculate recommended SIP amount"""
        if monthly_surplus <= 0:
            return {
                "recommended_monthly_sip": 0,
                "reasoning": "No surplus available for SIP investment"
            }
        
        # Base SIP recommendation based on surplus
        if risk_tolerance == "High":
            sip_percentage = 0.60  # 60% of surplus
        elif risk_tolerance == "Low":
            sip_percentage = 0.40  # 40% of surplus
        else:
            sip_percentage = 0.50  # 50% of surplus (balanced)
        
        recommended_sip = monthly_surplus * sip_percentage
        
        # Round to nearest 500 for practical SIP amounts
        recommended_sip = round(recommended_sip / 500) * 500
        
        return {
            "recommended_monthly_sip": float(recommended_sip),
            "percentage_of_surplus": sip_percentage * 100,
            "reasoning": f"Recommended SIP based on {risk_tolerance.lower()} risk tolerance and available surplus"
        }