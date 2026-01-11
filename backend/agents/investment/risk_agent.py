"""
Risk & Safety Agent

Evaluates downside risk and ensures safety constraints.
Can BLOCK aggressive paths if unsafe.
"""
from typing import Dict, Any, Optional


class RiskAgent:
    """
    Risk & Safety Agent
    
    Evaluates downside risk
    Ensures emergency fund logic
    Can BLOCK aggressive paths if unsafe
    """
    
    def __init__(self):
        self.agent_name = "RiskAgent"
    
    def assess_risk(
        self, 
        profiler_output: Dict[str, Any],
        router_output: Dict[str, Any],
        equity_output: Optional[Dict[str, Any]] = None,
        etf_output: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Assess risk and safety constraints
        
        Args:
            profiler_output: Output from ProfilerAgent
            router_output: Output from RouterAgent
            equity_output: Optional output from EquityAgent
            etf_output: Optional output from ETFAgent
            
        Returns:
            Dict with risk assessment and safety overrides
        """
        monthly_income = profiler_output.get("monthly_income", 0)
        monthly_expenses = profiler_output.get("monthly_expenses", 0)
        monthly_surplus = profiler_output.get("monthly_surplus", 0)
        income_stability = profiler_output.get("income_stability", "unknown")
        emergency_fund_months = profiler_output.get("emergency_fund_months", 0)
        selected_paths = router_output.get("selected_paths", [])
        
        # Safety checks
        safety_checks = self._perform_safety_checks(
            monthly_income, monthly_expenses, monthly_surplus,
            income_stability, emergency_fund_months, selected_paths
        )
        
        # Determine if paths should be blocked
        blocked_paths = []
        safety_override = False
        safety_reason = None
        
        if safety_checks["insufficient_surplus"]:
            blocked_paths.extend(["aggressive", "balanced"])
            safety_override = True
            safety_reason = "Insufficient monthly surplus for aggressive investment strategies"
        
        if safety_checks["unstable_income"] and "aggressive" in selected_paths:
            blocked_paths.append("aggressive")
            safety_override = True
            safety_reason = "Unstable income pattern makes aggressive strategies risky"
        
        if safety_checks["low_emergency_fund"] and "aggressive" in selected_paths:
            blocked_paths.append("aggressive")
            safety_override = True
            safety_reason = "Low emergency fund coverage - aggressive investments not recommended"
        
        # Calculate risk score
        risk_score = self._calculate_risk_score(
            monthly_surplus, monthly_income, income_stability, emergency_fund_months
        )
        
        # Generate safety recommendations
        safety_recommendations = self._generate_safety_recommendations(safety_checks, monthly_surplus)
        
        return {
            "agent": self.agent_name,
            "confidence": 0.90,  # High confidence in safety assessments
            "risk_score": risk_score,
            "safety_checks": safety_checks,
            "blocked_paths": blocked_paths,
            "safety_override": safety_override,
            "safety_reason": safety_reason,
            "safety_recommendations": safety_recommendations,
        }
    
    def _perform_safety_checks(
        self,
        monthly_income: float,
        monthly_expenses: float,
        monthly_surplus: float,
        income_stability: str,
        emergency_fund_months: float,
        selected_paths: list
    ) -> Dict[str, Any]:
        """Perform safety constraint checks"""
        checks = {
            "sufficient_income": monthly_income > monthly_expenses,
            "sufficient_surplus": monthly_surplus >= 5000,  # Minimum surplus threshold
            "insufficient_surplus": monthly_surplus < 5000,
            "stable_income": income_stability in ["very_stable", "stable"],
            "unstable_income": income_stability in ["volatile", "moderate"],
            "adequate_emergency_fund": emergency_fund_months >= 3.0,
            "low_emergency_fund": emergency_fund_months < 3.0,
        }
        
        return checks
    
    def _calculate_risk_score(
        self,
        monthly_surplus: float,
        monthly_income: float,
        income_stability: str,
        emergency_fund_months: float
    ) -> float:
        """Calculate overall risk score (0-100, lower is safer)"""
        risk_score = 50.0  # Base risk score
        
        # Adjust based on surplus
        if monthly_income > 0:
            surplus_ratio = monthly_surplus / monthly_income
            if surplus_ratio < 0.1:
                risk_score += 30  # High risk
            elif surplus_ratio < 0.2:
                risk_score += 15  # Medium-high risk
            elif surplus_ratio >= 0.3:
                risk_score -= 15  # Lower risk
        
        # Adjust based on income stability
        stability_scores = {
            "very_stable": -20,
            "stable": -10,
            "moderate": 10,
            "volatile": 25,
            "unknown": 0,
        }
        risk_score += stability_scores.get(income_stability, 0)
        
        # Adjust based on emergency fund
        if emergency_fund_months >= 6:
            risk_score -= 15
        elif emergency_fund_months >= 3:
            risk_score -= 5
        elif emergency_fund_months < 1:
            risk_score += 25
        
        return max(0, min(100, risk_score))
    
    def _generate_safety_recommendations(
        self, 
        safety_checks: Dict[str, Any],
        monthly_surplus: float
    ) -> list:
        """Generate safety recommendations"""
        recommendations = []
        
        if safety_checks["insufficient_surplus"]:
            recommendations.append({
                "priority": "high",
                "recommendation": "Build emergency fund first before investing",
                "reasoning": "Monthly surplus is insufficient for investment strategies"
            })
        
        if safety_checks["low_emergency_fund"]:
            recommendations.append({
                "priority": "high",
                "recommendation": "Maintain 3-6 months expenses as emergency fund",
                "reasoning": "Emergency fund provides financial safety net"
            })
        
        if safety_checks["unstable_income"]:
            recommendations.append({
                "priority": "medium",
                "recommendation": "Consider conservative investment approach due to income volatility",
                "reasoning": "Unstable income requires more conservative investment strategy"
            })
        
        if not recommendations:
            recommendations.append({
                "priority": "low",
                "recommendation": "Safety checks passed - proceed with recommended investment path",
                "reasoning": "Financial profile supports investment strategies"
            })
        
        return recommendations