"""
Equity (Stock Market) Agent

Provides high-level stock investing ideas with educational focus.
No specific stock picks - focuses on strategies and principles.
"""
from typing import Dict, Any


class EquityAgent:
    """
    Equity (Stock Market) Agent
    
    Gives high-level stock investing ideas
    Focuses on:
    - Index funds
    - Blue-chip stocks (general categories)
    - Sector diversification
    - Educational + advisory tone
    - NO specific stock picks
    """
    
    def __init__(self):
        self.agent_name = "EquityAgent"
    
    def analyze_equity(
        self, 
        profiler_output: Dict[str, Any],
        intent_output: Dict[str, Any],
        router_output: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze equity investment strategy
        
        Args:
            profiler_output: Output from ProfilerAgent
            intent_output: Output from IntentAgent
            router_output: Output from RouterAgent
            
        Returns:
            Dict with equity investment suggestions
        """
        risk_tolerance = profiler_output.get("risk_tolerance", "Medium")
        monthly_surplus = profiler_output.get("monthly_surplus", 0)
        primary_intent = intent_output.get("primary_intent", "wealth_growth")
        selected_paths = router_output.get("selected_paths", [])
        
        # Determine equity strategy
        strategy = self._determine_strategy(risk_tolerance, primary_intent, selected_paths)
        
        # Generate suggestions
        suggestions = self._generate_suggestions(strategy, monthly_surplus, risk_tolerance)
        
        # Calculate confidence
        confidence = 0.75 if monthly_surplus > 10000 else 0.65
        
        return {
            "agent": self.agent_name,
            "confidence": confidence,
            "strategy": strategy,
            "suggestions": suggestions,
            "risk_level": risk_tolerance.lower(),
            "educational_note": "All equity investments carry market risk. Past performance does not guarantee future results. Consider index funds for diversification.",
        }
    
    def _determine_strategy(
        self, 
        risk_tolerance: str, 
        primary_intent: str,
        selected_paths: list
    ) -> str:
        """Determine equity investment strategy"""
        if "aggressive" in selected_paths or risk_tolerance == "High":
            return "growth_focused"
        elif "balanced" in selected_paths or risk_tolerance == "Medium":
            return "diversified"
        else:
            return "conservative_index"
    
    def _generate_suggestions(
        self, 
        strategy: str, 
        monthly_surplus: float,
        risk_tolerance: str
    ) -> Dict[str, Any]:
        """Generate equity investment suggestions"""
        suggestions = {
            "focus_areas": [],
            "allocation_suggestion": None,
            "investment_approach": "",
            "educational_points": [],
        }
        
        if strategy == "growth_focused":
            suggestions["focus_areas"] = [
                "Broad-market index funds for core holdings",
                "Sector diversification across multiple industries",
                "Systematic Investment Plan (SIP) approach"
            ]
            suggestions["allocation_suggestion"] = "Consider allocating 60-70% of investment surplus to equities"
            suggestions["investment_approach"] = "Growth-oriented approach with focus on long-term wealth accumulation"
            suggestions["educational_points"] = [
                "Index funds provide broad market exposure with lower risk than individual stocks",
                "Dollar-cost averaging (SIP) helps reduce impact of market volatility",
                "Long-term perspective is essential for equity investments"
            ]
        elif strategy == "diversified":
            suggestions["focus_areas"] = [
                "Balanced index fund portfolio",
                "Mix of large-cap and mid-cap exposure",
                "Regular SIP for disciplined investing"
            ]
            suggestions["allocation_suggestion"] = "Consider allocating 40-50% of investment surplus to equities"
            suggestions["investment_approach"] = "Balanced approach with focus on steady growth and diversification"
            suggestions["educational_points"] = [
                "Diversification across market caps helps balance risk and return",
                "Index funds eliminate need for stock picking while providing market returns",
                "Regular investing discipline is key to long-term success"
            ]
        else:  # conservative_index
            suggestions["focus_areas"] = [
                "Large-cap index funds for stability",
                "Blue-chip focused funds (general category guidance)",
                "Low-volatility equity exposure"
            ]
            suggestions["allocation_suggestion"] = "Consider allocating 20-30% of investment surplus to equities"
            suggestions["investment_approach"] = "Conservative equity exposure for capital growth with lower volatility"
            suggestions["educational_points"] = [
                "Large-cap stocks historically show lower volatility than small-cap",
                "Index funds provide instant diversification",
                "Conservative equity allocation can help preserve capital while earning growth"
            ]
        
        return suggestions