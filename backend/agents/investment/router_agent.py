"""
Path Router Agent (CORE)

Chooses investment paths dynamically based on user profile and intent.
Routes data to relevant specialized agents.
"""
from typing import Dict, Any, List, Optional


class RouterAgent:
    """
    Path Router Agent (CORE)
    
    Chooses ONE or MORE paths:
    - Conservative Path
    - Balanced Path
    - Aggressive Growth Path
    - Beginner Learning Path
    - Short-Term Goal Path
    
    Routes data to relevant agents.
    """
    
    def __init__(self):
        self.agent_name = "RouterAgent"
        self.paths = {
            "conservative": {
                "name": "Conservative Path",
                "agents": ["RiskAgent", "ETFAgent"],
                "risk_level": "Low",
                "description": "Capital protection with low-risk investments"
            },
            "balanced": {
                "name": "Balanced Path",
                "agents": ["EquityAgent", "ETFAgent", "RiskAgent"],
                "risk_level": "Medium",
                "description": "Diversified approach with balanced risk"
            },
            "aggressive": {
                "name": "Aggressive Growth Path",
                "agents": ["EquityAgent", "RiskAgent"],
                "risk_level": "High",
                "description": "Growth-focused with higher risk tolerance"
            },
            "beginner": {
                "name": "Beginner Learning Path",
                "agents": ["ETFAgent", "RiskAgent"],
                "risk_level": "Low",
                "description": "Educational approach with low-risk starter investments"
            },
            "short_term": {
                "name": "Short-Term Goal Path",
                "agents": ["ETFAgent", "RiskAgent"],
                "risk_level": "Low",
                "description": "Low-risk approach for near-term goals"
            }
        }
    
    def route_paths(
        self, 
        profiler_output: Dict[str, Any],
        intent_output: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Route user to appropriate investment path(s)
        
        Args:
            profiler_output: Output from ProfilerAgent
            intent_output: Output from IntentAgent
            
        Returns:
            Dict with selected paths and routing instructions
        """
        primary_intent = intent_output.get("primary_intent", "wealth_growth")
        risk_tolerance = profiler_output.get("risk_tolerance", "Medium")
        investor_type = profiler_output.get("investor_type", "")
        monthly_surplus = profiler_output.get("monthly_surplus", 0)
        goals = profiler_output.get("goals", {})
        goal_timeline = goals.get("goal_timeline_years")
        is_beginner = "learning" in intent_output.get("secondary_intents", [])
        
        # Determine paths
        selected_paths = self._select_paths(
            primary_intent, risk_tolerance, investor_type, 
            monthly_surplus, goal_timeline, is_beginner
        )
        
        # Determine which agents to invoke
        agents_to_invoke = self._determine_agents(selected_paths)
        
        # Generate routing reasoning
        reasoning = self._generate_routing_reasoning(
            selected_paths, primary_intent, risk_tolerance, is_beginner
        )
        
        return {
            "agent": self.agent_name,
            "confidence": 0.80,
            "selected_paths": selected_paths,
            "path_details": [self.paths[path] for path in selected_paths],
            "agents_to_invoke": agents_to_invoke,
            "routing_reasoning": reasoning,
        }
    
    def _select_paths(
        self,
        primary_intent: str,
        risk_tolerance: str,
        investor_type: str,
        monthly_surplus: float,
        goal_timeline: Optional[int],
        is_beginner: bool
    ) -> List[str]:
        """Select appropriate paths based on user profile"""
        paths = []
        
        # Beginner always gets learning path first
        if is_beginner or monthly_surplus < 5000:
            paths.append("beginner")
            return paths  # Return early - beginners get simplified path
        
        # Short-term goals (< 3 years)
        if goal_timeline and goal_timeline < 3:
            paths.append("short_term")
            return paths  # Short-term goals get conservative approach
        
        # Main path selection based on intent and risk tolerance
        if primary_intent == "capital_protection" or risk_tolerance == "Low":
            paths.append("conservative")
        elif primary_intent == "wealth_growth":
            if risk_tolerance == "High":
                paths.append("aggressive")
            else:
                paths.append("balanced")
        elif primary_intent == "passive_income":
            paths.append("balanced")  # Passive income requires balanced approach
        else:
            paths.append("balanced")  # Default to balanced
        
        return paths
    
    def _determine_agents(self, selected_paths: List[str]) -> List[str]:
        """Determine which agents to invoke based on selected paths"""
        agents_set = set()
        
        for path_key in selected_paths:
            path_info = self.paths.get(path_key, {})
            agents = path_info.get("agents", [])
            agents_set.update(agents)
        
        # Always include RiskAgent for safety
        agents_set.add("RiskAgent")
        
        return list(agents_set)
    
    def _generate_routing_reasoning(
        self,
        selected_paths: List[str],
        primary_intent: str,
        risk_tolerance: str,
        is_beginner: bool
    ) -> str:
        """Generate human-readable routing reasoning"""
        path_names = [self.paths[path]["name"] for path in selected_paths]
        
        reasoning_parts = []
        
        if is_beginner:
            reasoning_parts.append("User profile indicates beginner status")
        
        reasoning_parts.append(f"Primary intent: {primary_intent.replace('_', ' ')}")
        reasoning_parts.append(f"Risk tolerance: {risk_tolerance}")
        reasoning_parts.append(f"Selected path(s): {', '.join(path_names)}")
        
        return ". ".join(reasoning_parts)