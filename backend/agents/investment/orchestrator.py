"""
Investment Orchestrator

Coordinates the multi-agent investment advisory workflow.
Implements the path-based agent communication system.
"""
from typing import Dict, Any, Optional
from ...db import db
from ...models import InvestmentRecommendation
from .profiler_agent import ProfilerAgent
from .intent_agent import IntentAgent
from .router_agent import RouterAgent
from .equity_agent import EquityAgent
from .etf_agent import ETFAgent
from .risk_agent import RiskAgent
from .consensus_agent import ConsensusAgent


class InvestmentOrchestrator:
    """
    Investment Orchestrator
    
    Coordinates the multi-agent investment advisory system:
    1. User Profiling Agent
    2. Intent Detection Agent
    3. Path Router Agent
    4. Specialized Investment Agents (Equity, ETF, Risk)
    5. Consensus & Reasoning Agent
    
    Agents communicate via structured JSON messages.
    """
    
    def __init__(self):
        self.profiler = ProfilerAgent()
        self.intent = IntentAgent()
        self.router = RouterAgent()
        self.equity = EquityAgent()
        self.etf = ETFAgent()
        self.risk = RiskAgent()
        self.consensus = ConsensusAgent()
    
    def generate_recommendation(self, user_id: int) -> Dict[str, Any]:
        """
        Execute full multi-agent workflow and generate investment recommendation
        
        Workflow:
        1. ProfilerAgent: Analyze user financial state
        2. IntentAgent: Detect investment intent
        3. RouterAgent: Select investment path(s)
        4. Specialized Agents: Generate recommendations based on path
        5. RiskAgent: Assess safety and risk
        6. ConsensusAgent: Reach consensus and generate final recommendation
        
        Args:
            user_id: User ID to analyze
            
        Returns:
            Dict with final recommendation and all agent outputs
        """
        try:
            # STEP 1: Profile user
            profiler_output = self.profiler.analyze_user(user_id)
            
            # STEP 2: Detect intent
            intent_output = self.intent.detect_intent(profiler_output)
            
            # STEP 3: Route to paths
            router_output = self.router.route_paths(profiler_output, intent_output)
            
            # STEP 4: Invoke specialized agents based on router
            selected_paths = router_output.get("selected_paths", [])
            agents_to_invoke = router_output.get("agents_to_invoke", [])
            
            equity_output = None
            etf_output = None
            
            if "EquityAgent" in agents_to_invoke:
                equity_output = self.equity.analyze_equity(
                    profiler_output, intent_output, router_output
                )
            
            if "ETFAgent" in agents_to_invoke:
                etf_output = self.etf.analyze_etf(
                    profiler_output, intent_output, router_output
                )
            
            # STEP 5: Assess risk (always invoked)
            risk_output = self.risk.assess_risk(
                profiler_output, router_output, equity_output, etf_output
            )
            
            # STEP 6: Reach consensus
            consensus_output = self.consensus.reach_consensus(
                profiler_output, intent_output, router_output,
                risk_output, equity_output, etf_output
            )
            
            # Create recommendation record
            recommendation = self._create_recommendation(
                user_id, profiler_output, intent_output, router_output,
                equity_output, etf_output, risk_output, consensus_output
            )
            
            # Return complete result
            return {
                "status": "success",
                "recommendation_id": recommendation.id,
                "recommendation": recommendation.to_dict(),
                "agent_outputs": {
                    "profiler": profiler_output,
                    "intent": intent_output,
                    "router": router_output,
                    "equity": equity_output,
                    "etf": etf_output,
                    "risk": risk_output,
                    "consensus": consensus_output,
                },
            }
            
        except Exception as e:
            print(f"Error in investment orchestrator: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "recommendation": None,
            }
    
    def _create_recommendation(
        self,
        user_id: int,
        profiler_output: Dict[str, Any],
        intent_output: Dict[str, Any],
        router_output: Dict[str, Any],
        equity_output: Optional[Dict[str, Any]],
        etf_output: Optional[Dict[str, Any]],
        risk_output: Dict[str, Any],
        consensus_output: Dict[str, Any]
    ) -> InvestmentRecommendation:
        """Create and save investment recommendation to database"""
        recommendations = consensus_output.get("recommendations", {})
        
        recommendation = InvestmentRecommendation(
            user_id=user_id,
            selected_path=consensus_output.get("selected_path", ""),
            selected_paths=consensus_output.get("selected_paths", []),
            investor_type=profiler_output.get("investor_type"),
            risk_tolerance=profiler_output.get("risk_tolerance"),
            primary_intent=intent_output.get("primary_intent"),
            profiler_output=profiler_output,
            intent_output=intent_output,
            router_output=router_output,
            equity_output=equity_output,
            etf_output=etf_output,
            risk_output=risk_output,
            recommendations=recommendations,
            reasoning=consensus_output.get("reasoning", ""),
            agent_reasoning=consensus_output.get("agent_reasoning"),
            safety_override=consensus_output.get("safety_override", False),
            safety_reason=consensus_output.get("safety_reason"),
        )
        
        db.session.add(recommendation)
        db.session.commit()
        
        return recommendation
    
    def get_latest_recommendation(self, user_id: int) -> Optional[InvestmentRecommendation]:
        """Get latest investment recommendation for user"""
        return InvestmentRecommendation.query.filter_by(user_id=user_id)\
            .order_by(InvestmentRecommendation.created_at.desc())\
            .first()