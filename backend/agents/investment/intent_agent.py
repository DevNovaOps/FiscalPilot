"""
Intent Detection Agent

Determines user's primary investment intent based on financial profile.
Rule-based logic - no questions asked unless absolutely necessary.
"""
from typing import Dict, Any


class IntentAgent:
    """
    Intent Detection Agent
    
    Determines intent from user profile:
    - Wealth growth
    - Passive income
    - Capital protection
    - Learning / beginner investing
    
    Does NOT ask user questions unless needed.
    """
    
    def __init__(self):
        self.agent_name = "IntentAgent"
    
    def detect_intent(self, profiler_output: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect user's primary investment intent
        
        Args:
            profiler_output: Output from ProfilerAgent
            
        Returns:
            Dict with detected intent and confidence
        """
        investor_type = profiler_output.get("investor_type", "")
        risk_tolerance = profiler_output.get("risk_tolerance", "Medium")
        monthly_surplus = profiler_output.get("monthly_surplus", 0)
        goals = profiler_output.get("goals", {})
        primary_goal = goals.get("primary_goal")
        
        # Determine intent based on profile
        intent = self._infer_intent(investor_type, risk_tolerance, monthly_surplus, primary_goal)
        
        # Calculate confidence
        confidence = self._calculate_confidence(profiler_output, intent)
        
        return {
            "agent": self.agent_name,
            "confidence": confidence,
            "primary_intent": intent["type"],
            "intent_reasoning": intent["reasoning"],
            "secondary_intents": intent.get("secondary", []),
        }
    
    def _infer_intent(
        self, 
        investor_type: str, 
        risk_tolerance: str,
        monthly_surplus: float,
        primary_goal: str
    ) -> Dict[str, Any]:
        """Infer intent from profile data"""
        
        # Check if beginner (low surplus or first-time investor signals)
        is_beginner = monthly_surplus < 5000  # Threshold for beginner
        
        # Primary intent based on goals
        if primary_goal:
            goal_intent_map = {
                "retirement": "wealth_growth",
                "house": "wealth_growth",
                "education": "wealth_growth",
                "emergency_fund": "capital_protection",
                "passive_income": "passive_income",
                "wealth_accumulation": "wealth_growth",
            }
            primary = goal_intent_map.get(primary_goal, "wealth_growth")
        else:
            # Infer from investor type and risk tolerance
            if "Growth" in investor_type or risk_tolerance == "High":
                primary = "wealth_growth"
            elif "Conservative" in investor_type or risk_tolerance == "Low":
                primary = "capital_protection"
            elif monthly_surplus > 20000:  # High surplus might indicate passive income interest
                primary = "passive_income"
            else:
                primary = "wealth_growth"  # Default
        
        # Add learning intent if beginner
        secondary = []
        if is_beginner:
            secondary.append("learning")
        
        # Determine reasoning
        reasoning_parts = []
        if primary_goal:
            reasoning_parts.append(f"Primary goal '{primary_goal}' suggests {primary.replace('_', ' ')} intent")
        else:
            reasoning_parts.append(f"Inferred {primary.replace('_', ' ')} intent from {investor_type} profile")
        
        if is_beginner:
            reasoning_parts.append("Low surplus indicates beginner status - learning intent added")
        
        reasoning = ". ".join(reasoning_parts)
        
        return {
            "type": primary,
            "reasoning": reasoning,
            "secondary": secondary,
        }
    
    def _calculate_confidence(self, profiler_output: Dict, intent: Dict) -> float:
        """Calculate confidence in intent detection"""
        confidence = 0.7  # Base confidence
        
        # Higher confidence if goals are present
        goals = profiler_output.get("goals", {})
        if goals.get("has_goals"):
            confidence += 0.15
        
        # Higher confidence if clear investor type
        investor_type = profiler_output.get("investor_type", "")
        if investor_type and investor_type != "Emerging Investor":
            confidence += 0.1
        
        # Lower confidence if multiple secondary intents
        if len(intent.get("secondary", [])) > 1:
            confidence -= 0.1
        
        return min(0.95, max(0.5, confidence))