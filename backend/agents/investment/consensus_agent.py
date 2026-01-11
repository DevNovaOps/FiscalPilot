"""
Consensus & Reasoning Agent

Collects outputs from all agents, resolves conflicts, produces final structured advice.
Explains "WHY this path was chosen".
"""
from typing import Dict, Any, List, Optional


class ConsensusAgent:
    """
    Consensus & Reasoning Agent
    
    Collects outputs from all agents
    Resolves conflicts
    Produces final structured advice
    Explains "WHY this path was chosen"
    """
    
    def __init__(self):
        self.agent_name = "ConsensusAgent"
    
    def reach_consensus(
        self,
        profiler_output: Dict[str, Any],
        intent_output: Dict[str, Any],
        router_output: Dict[str, Any],
        risk_output: Dict[str, Any],
        equity_output: Optional[Dict[str, Any]] = None,
        etf_output: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Reach consensus from all agent outputs
        
        Args:
            profiler_output: Output from ProfilerAgent
            intent_output: Output from IntentAgent
            router_output: Output from RouterAgent
            risk_output: Output from RiskAgent
            equity_output: Optional output from EquityAgent
            etf_output: Optional output from ETFAgent
            
        Returns:
            Dict with final consensus recommendation
        """
        # Apply safety overrides from RiskAgent
        selected_paths = router_output.get("selected_paths", [])
        blocked_paths = risk_output.get("blocked_paths", [])
        safety_override = risk_output.get("safety_override", False)
        
        # Filter out blocked paths
        final_paths = [path for path in selected_paths if path not in blocked_paths]
        
        # If all paths blocked, default to conservative
        if not final_paths and selected_paths:
            final_paths = ["conservative"]
            safety_override = True
        
        # Get primary path (first in list)
        primary_path = final_paths[0] if final_paths else "conservative"
        
        # Generate final recommendations
        recommendations = self._generate_recommendations(
            profiler_output, intent_output, router_output,
            risk_output, equity_output, etf_output, final_paths, primary_path
        )
        
        # Generate reasoning
        reasoning = self._generate_reasoning(
            profiler_output, intent_output, router_output,
            risk_output, equity_output, etf_output, final_paths, primary_path, safety_override
        )
        
        # Generate agent reasoning summary
        agent_reasoning = self._generate_agent_reasoning(
            profiler_output, intent_output, router_output,
            risk_output, equity_output, etf_output
        )
        
        # Calculate overall confidence
        confidence = self._calculate_confidence(
            profiler_output, intent_output, router_output, risk_output, equity_output, etf_output
        )
        
        return {
            "agent": self.agent_name,
            "confidence": confidence,
            "selected_path": self._get_path_name(primary_path),
            "selected_paths": [self._get_path_name(p) for p in final_paths],
            "recommendations": recommendations,
            "reasoning": reasoning,
            "agent_reasoning": agent_reasoning,
            "safety_override": safety_override,
            "safety_reason": risk_output.get("safety_reason"),
        }
    
    def _generate_recommendations(
        self,
        profiler_output: Dict[str, Any],
        intent_output: Dict[str, Any],
        router_output: Dict[str, Any],
        risk_output: Dict[str, Any],
        equity_output: Optional[Dict[str, Any]],
        etf_output: Optional[Dict[str, Any]],
        final_paths: List[str],
        primary_path: str
    ) -> Dict[str, Any]:
        """Generate structured final recommendations"""
        recommendations = {
            "primary_path": self._get_path_name(primary_path),
            "all_paths": [self._get_path_name(p) for p in final_paths],
            "investment_suggestions": [],
            "actionable_steps": [],
            "risk_warnings": [],
        }
        
        # Add equity recommendations if available
        if equity_output:
            equity_suggestions = equity_output.get("suggestions", {})
            recommendations["investment_suggestions"].append({
                "type": "equity",
                "strategy": equity_output.get("strategy"),
                "allocation": equity_suggestions.get("allocation_suggestion"),
                "focus_areas": equity_suggestions.get("focus_areas", []),
                "educational_points": equity_suggestions.get("educational_points", []),
            })
            recommendations["actionable_steps"].append({
                "step": "Research broad-market index funds",
                "reasoning": "Index funds provide diversification without stock-picking risk"
            })
        
        # Add ETF/Mutual Fund recommendations if available
        if etf_output:
            etf_suggestions = etf_output.get("suggestions", {})
            sip_rec = etf_output.get("sip_recommendation", {})
            recommendations["investment_suggestions"].append({
                "type": "etf_mutual_funds",
                "strategy": etf_output.get("strategy"),
                "allocation": etf_suggestions.get("allocation_suggestion"),
                "sip_amount": sip_rec.get("recommended_monthly_sip"),
                "fund_categories": etf_suggestions.get("fund_categories", []),
                "educational_points": etf_suggestions.get("educational_points", []),
            })
            if sip_rec.get("recommended_monthly_sip", 0) > 0:
                recommendations["actionable_steps"].append({
                    "step": f"Start SIP of ₹{sip_rec['recommended_monthly_sip']:,.0f} per month",
                    "reasoning": "Systematic Investment Plan helps in disciplined investing"
                })
        
        # Add risk warnings
        safety_recs = risk_output.get("safety_recommendations", [])
        for rec in safety_recs:
            if rec.get("priority") == "high":
                recommendations["risk_warnings"].append({
                    "warning": rec.get("recommendation"),
                    "reasoning": rec.get("reasoning"),
                })
        
        # Add general actionable steps
        if not recommendations["actionable_steps"]:
            recommendations["actionable_steps"].append({
                "step": "Build emergency fund (3-6 months expenses)",
                "reasoning": "Emergency fund provides financial security"
            })
            recommendations["actionable_steps"].append({
                "step": "Research investment options based on your risk profile",
                "reasoning": "Understanding options helps make informed decisions"
            })
        
        return recommendations
    
    def _generate_reasoning(
        self,
        profiler_output: Dict[str, Any],
        intent_output: Dict[str, Any],
        router_output: Dict[str, Any],
        risk_output: Dict[str, Any],
        equity_output: Optional[Dict[str, Any]],
        etf_output: Optional[Dict[str, Any]],
        final_paths: List[str],
        primary_path: str,
        safety_override: bool
    ) -> str:
        """Generate human-readable reasoning for path selection"""
        reasoning_parts = []
        
        # Start with investor profile
        investor_type = profiler_output.get("investor_type", "")
        risk_tolerance = profiler_output.get("risk_tolerance", "")
        reasoning_parts.append(f"Based on your profile as a {investor_type} with {risk_tolerance} risk tolerance")
        
        # Add intent reasoning
        primary_intent = intent_output.get("primary_intent", "")
        reasoning_parts.append(f"your primary intent is {primary_intent.replace('_', ' ')}")
        
        # Add path reasoning
        path_name = self._get_path_name(primary_path)
        routing_reasoning = router_output.get("routing_reasoning", "")
        reasoning_parts.append(f"the {path_name} was selected")
        
        # Add safety override reasoning if applicable
        if safety_override:
            safety_reason = risk_output.get("safety_reason", "")
            if safety_reason:
                reasoning_parts.append(f"Safety adjustments: {safety_reason}")
        
        # Add agent contributions
        if equity_output:
            reasoning_parts.append("Equity agent recommended index-focused approach")
        if etf_output:
            sip_rec = etf_output.get("sip_recommendation", {})
            if sip_rec.get("recommended_monthly_sip", 0) > 0:
                reasoning_parts.append(f"SIP strategy recommended for disciplined investing")
        
        return ". ".join(reasoning_parts) + "."
    
    def _generate_agent_reasoning(
        self,
        profiler_output: Dict[str, Any],
        intent_output: Dict[str, Any],
        router_output: Dict[str, Any],
        risk_output: Dict[str, Any],
        equity_output: Optional[Dict[str, Any]],
        etf_output: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate summary of each agent's reasoning"""
        agent_reasoning = {
            "profiler": {
                "investor_type": profiler_output.get("investor_type"),
                "risk_tolerance": profiler_output.get("risk_tolerance"),
                "monthly_surplus": profiler_output.get("monthly_surplus"),
            },
            "intent": {
                "primary_intent": intent_output.get("primary_intent"),
                "confidence": intent_output.get("confidence"),
            },
            "router": {
                "selected_paths": router_output.get("selected_paths", []),
                "routing_reasoning": router_output.get("routing_reasoning"),
            },
            "risk": {
                "risk_score": risk_output.get("risk_score"),
                "safety_override": risk_output.get("safety_override"),
                "blocked_paths": risk_output.get("blocked_paths", []),
            },
        }
        
        if equity_output:
            agent_reasoning["equity"] = {
                "strategy": equity_output.get("strategy"),
                "confidence": equity_output.get("confidence"),
            }
        
        if etf_output:
            agent_reasoning["etf"] = {
                "strategy": etf_output.get("strategy"),
                "confidence": etf_output.get("confidence"),
                "sip_recommended": etf_output.get("sip_recommendation", {}).get("recommended_monthly_sip", 0) > 0,
            }
        
        return agent_reasoning
    
    def _calculate_confidence(
        self,
        profiler_output: Dict[str, Any],
        intent_output: Dict[str, Any],
        router_output: Dict[str, Any],
        risk_output: Dict[str, Any],
        equity_output: Optional[Dict[str, Any]],
        etf_output: Optional[Dict[str, Any]]
    ) -> float:
        """Calculate overall confidence in recommendations"""
        confidences = [
            profiler_output.get("confidence", 0.8),
            intent_output.get("confidence", 0.7),
            router_output.get("confidence", 0.8),
            risk_output.get("confidence", 0.9),
        ]
        
        if equity_output:
            confidences.append(equity_output.get("confidence", 0.75))
        
        if etf_output:
            confidences.append(etf_output.get("confidence", 0.80))
        
        # Average confidence
        avg_confidence = sum(confidences) / len(confidences)
        
        return round(avg_confidence, 2)
    
    def _get_path_name(self, path_key: str) -> str:
        """Get human-readable path name"""
        path_names = {
            "conservative": "Conservative Path",
            "balanced": "Balanced Path",
            "aggressive": "Aggressive Growth Path",
            "beginner": "Beginner Learning Path",
            "short_term": "Short-Term Goal Path",
        }
        return path_names.get(path_key, path_key.title() + " Path")