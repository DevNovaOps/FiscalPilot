"""
LangGraph Orchestrator
Coordinates all agents in the Fiscal Pilot system
"""
from typing import Dict, Any, TypedDict, List
from langgraph.graph import StateGraph, END
from .transaction_agent import TransactionIntelligenceAgent
from .behavior_agent import FinancialBehaviorAgent
from .investment_agent import InvestmentKnowledgeAgent
from .decision_agent import DecisionConfidenceAgent
from .explainability_agent import ExplainabilityAgent
from .compliance_agent import ComplianceGuardAgent
from .tools import TransactionTools, FinancialAnalysisTools
from ..db import db
from ..models.ai_decision import AIDecision
from ..models.risk_profile import RiskProfile
from ..models.transaction import Transaction


class AgentState(TypedDict):
    """State passed between agents in the graph"""
    user_id: int
    transactions: List[Dict[str, Any]]
    categorized_transactions: List[Dict[str, Any]]
    financial_analysis: Dict[str, Any]
    risk_profile: Dict[str, Any]
    user_preferences: Dict[str, Any]
    investment_education: Dict[str, Any]
    decision: Dict[str, Any]
    explanation: Dict[str, Any]
    compliance_check: Dict[str, Any]
    final_output: Dict[str, Any]
    errors: List[str]


class AgentOrchestrator:
    """
    Main orchestrator using LangGraph to coordinate agents
    
    Flow:
    1. Transaction Intelligence Agent
    2. Financial Behavior Agent (parallel with Transaction)
    3. Investment Knowledge Agent
    4. Decision Confidence Agent
    5. Explainability Agent
    6. Compliance Guard Agent (runs in parallel on all outputs)
    """
    
    def __init__(self):
        """Initialize all agents"""
        self.transaction_agent = TransactionIntelligenceAgent()
        self.behavior_agent = FinancialBehaviorAgent()
        self.investment_agent = InvestmentKnowledgeAgent()
        self.decision_agent = DecisionConfidenceAgent()
        self.explainability_agent = ExplainabilityAgent()
        self.compliance_agent = ComplianceGuardAgent()
        
        # Build the graph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph state graph"""
        workflow = StateGraph(AgentState)
        
        # Define nodes
        workflow.add_node("categorize_transactions", self._categorize_transactions_node)
        workflow.add_node("analyze_behavior", self._analyze_behavior_node)
        workflow.add_node("get_investment_education", self._get_investment_education_node)
        workflow.add_node("make_decision", self._make_decision_node)
        workflow.add_node("explain_decision", self._explain_decision_node)
        workflow.add_node("check_compliance", self._check_compliance_node)
        workflow.add_node("finalize_output", self._finalize_output_node)
        
        # Define edges
        workflow.set_entry_point("categorize_transactions")
        
        workflow.add_edge("categorize_transactions", "analyze_behavior")
        workflow.add_edge("analyze_behavior", "get_investment_education")
        workflow.add_edge("get_investment_education", "make_decision")
        workflow.add_edge("make_decision", "explain_decision")
        
        # Compliance runs on decision output (can run in parallel in real LangGraph)
        workflow.add_edge("explain_decision", "check_compliance")
        workflow.add_edge("check_compliance", "finalize_output")
        workflow.add_edge("finalize_output", END)
        
        return workflow.compile()
    
    def _categorize_transactions_node(self, state: AgentState) -> AgentState:
        """Node: Categorize transactions"""
        try:
            transactions = state.get("transactions", [])
            if transactions:
                result = self.transaction_agent.analyze_transactions(transactions)
                state["categorized_transactions"] = result.get("categorized_transactions", transactions)
            else:
                state["categorized_transactions"] = []
        except Exception as e:
            state.setdefault("errors", []).append(f"Transaction categorization error: {str(e)}")
        return state
    
    def _analyze_behavior_node(self, state: AgentState) -> AgentState:
        """Node: Analyze financial behavior and calculate risk profile"""
        try:
            user_id = state["user_id"]
            
            # Get financial metrics
            savings_data = FinancialAnalysisTools.calculate_savings_rate(user_id, months=6)
            monthly_summary = TransactionTools.get_monthly_summary(user_id, months=6)
            recurring_data = FinancialAnalysisTools.detect_recurring_expenses(user_id)
            
            # Calculate discretionary spending
            transactions = TransactionTools.get_user_transactions(user_id, days=180)
            total_expenses = sum(abs(float(t.get("amount", 0))) for t in transactions 
                               if t.get("transaction_type") == "expense")
            discretionary_spend = sum(abs(float(t.get("amount", 0))) for t in transactions 
                                    if t.get("is_discretionary", False))
            discretionary_percentage = (discretionary_spend / total_expenses * 100) if total_expenses > 0 else 0
            
            financial_data = {
                **savings_data,
                "monthly_summary": monthly_summary,
                "recurring_total": recurring_data.get("recurring_total", 0),
                "discretionary_percentage": discretionary_percentage,
            }
            
            # Assess risk profile
            risk_profile = self.behavior_agent.assess_risk_profile(financial_data)
            
            state["financial_analysis"] = financial_data
            state["risk_profile"] = risk_profile
            
            # Save risk profile to database
            self._save_risk_profile(state["user_id"], risk_profile)
            
        except Exception as e:
            state.setdefault("errors", []).append(f"Behavior analysis error: {str(e)}")
        return state
    
    def _get_investment_education_node(self, state: AgentState) -> AgentState:
        """Node: Get educational investment information"""
        try:
            risk_level = state.get("risk_profile", {}).get("risk_level", "Medium")
            asset_classes = state.get("user_preferences", {}).get("interested_asset_classes", None)
            
            education = self.investment_agent.get_investment_education(risk_level, asset_classes)
            state["investment_education"] = education
            
        except Exception as e:
            state.setdefault("errors", []).append(f"Investment education error: {str(e)}")
        return state
    
    def _make_decision_node(self, state: AgentState) -> AgentState:
        """Node: Make decision about suitable investments"""
        try:
            risk_profile = state.get("risk_profile", {})
            financial_analysis = state.get("financial_analysis", {})
            user_preferences = state.get("user_preferences", {})
            investment_info = state.get("investment_education", {})
            
            decision = self.decision_agent.make_decision(
                risk_profile=risk_profile,
                behavior_data=financial_analysis,
                user_goals=user_preferences,
                investment_info=investment_info
            )
            state["decision"] = decision
            
        except Exception as e:
            state.setdefault("errors", []).append(f"Decision making error: {str(e)}")
        return state
    
    def _explain_decision_node(self, state: AgentState) -> AgentState:
        """Node: Explain the decision"""
        try:
            decision = state.get("decision", {})
            risk_profile = state.get("risk_profile", {})
            financial_analysis = state.get("financial_analysis", {})
            
            explanation = self.explainability_agent.explain_decision(
                decision_data=decision,
                risk_profile=risk_profile,
                financial_context=financial_analysis
            )
            state["explanation"] = explanation
            
        except Exception as e:
            state.setdefault("errors", []).append(f"Explanation error: {str(e)}")
        return state
    
    def _check_compliance_node(self, state: AgentState) -> AgentState:
        """Node: Check compliance of all outputs"""
        try:
            # Check decision output
            decision = state.get("decision", {})
            compliance_decision = self.compliance_agent.check_compliance(
                decision, "DecisionConfidenceAgent"
            )
            
            # Check explanation output
            explanation = state.get("explanation", {})
            compliance_explanation = self.compliance_agent.check_compliance(
                explanation, "ExplainabilityAgent"
            )
            
            state["compliance_check"] = {
                "decision_compliance": compliance_decision,
                "explanation_compliance": compliance_explanation,
                "all_compliant": (
                    compliance_decision.get("compliant", True) and
                    compliance_explanation.get("compliant", True)
                ),
            }
            
            # Block if non-compliant
            if not state["compliance_check"]["all_compliant"]:
                state.setdefault("errors", []).append("Compliance check failed")
            
        except Exception as e:
            state.setdefault("errors", []).append(f"Compliance check error: {str(e)}")
        return state
    
    def _finalize_output_node(self, state: AgentState) -> AgentState:
        """Node: Finalize output and log decisions"""
        try:
            user_id = state["user_id"]
            
            # Log AI decisions for audit
            self._log_ai_decision(user_id, "risk_assessment", state.get("risk_profile", {}))
            self._log_ai_decision(user_id, "investment_suitability", state.get("decision", {}))
            self._log_ai_decision(user_id, "explanation", state.get("explanation", {}))
            
            # Build final output
            state["final_output"] = {
                "risk_profile": state.get("risk_profile", {}),
                "financial_analysis": state.get("financial_analysis", {}),
                "investment_education": state.get("investment_education", {}),
                "decision": state.get("decision", {}),
                "explanation": state.get("explanation", {}),
                "compliance_check": state.get("compliance_check", {}),
                "success": len(state.get("errors", [])) == 0,
                "errors": state.get("errors", []),
            }
            
        except Exception as e:
            state.setdefault("errors", []).append(f"Finalization error: {str(e)}")
        return state
    
    def run(self, user_id: int, transactions: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Run the complete agent orchestration
        
        Args:
            user_id: User ID
            transactions: Optional list of transactions (if None, fetched from DB)
            
        Returns:
            Complete analysis output
        """
        # Initialize state
        if transactions is None:
            transactions = TransactionTools.get_user_transactions(user_id, days=180)
        
        user_prefs = FinancialAnalysisTools.get_user_preferences(user_id)
        if user_prefs is None:
            user_prefs = {}
        
        initial_state: AgentState = {
            "user_id": user_id,
            "transactions": transactions,
            "categorized_transactions": [],
            "financial_analysis": {},
            "risk_profile": {},
            "user_preferences": user_prefs,
            "investment_education": {},
            "decision": {},
            "explanation": {},
            "compliance_check": {},
            "final_output": {},
            "errors": [],
        }
        
        # Run the graph
        final_state = self.graph.invoke(initial_state)
        
        return final_state.get("final_output", {})
    
    def _save_risk_profile(self, user_id: int, risk_profile: Dict[str, Any]):
        """Save risk profile to database"""
        try:
            existing = RiskProfile.query.filter_by(user_id=user_id).first()
            
            if existing:
                # Update existing
                existing.risk_score = risk_profile.get("risk_score", 50)
                existing.risk_level = risk_profile.get("risk_level", "Medium")
                existing.income_stability_score = risk_profile.get("income_stability_score")
                existing.expense_volatility_score = risk_profile.get("expense_volatility_score")
                existing.savings_rate = risk_profile.get("savings_rate")
                existing.emergency_fund_months = risk_profile.get("emergency_fund_months")
                existing.discretionary_spend_percentage = risk_profile.get("discretionary_spend_percentage")
                existing.recurring_obligations_percentage = risk_profile.get("recurring_obligations_percentage")
                existing.explanation = risk_profile.get("reasoning", "")
                existing.key_factors = risk_profile.get("key_factors", [])
                existing.updated_at = db.func.now()
            else:
                # Create new
                new_profile = RiskProfile(
                    user_id=user_id,
                    risk_score=risk_profile.get("risk_score", 50),
                    risk_level=risk_profile.get("risk_level", "Medium"),
                    income_stability_score=risk_profile.get("income_stability_score"),
                    expense_volatility_score=risk_profile.get("expense_volatility_score"),
                    savings_rate=risk_profile.get("savings_rate"),
                    emergency_fund_months=risk_profile.get("emergency_fund_months"),
                    discretionary_spend_percentage=risk_profile.get("discretionary_spend_percentage"),
                    recurring_obligations_percentage=risk_profile.get("recurring_obligations_percentage"),
                    explanation=risk_profile.get("reasoning", ""),
                    key_factors=risk_profile.get("key_factors", []),
                )
                db.session.add(new_profile)
            
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error saving risk profile: {str(e)}")
    
    def _log_ai_decision(self, user_id: int, decision_type: str, decision_data: Dict[str, Any]):
        """Log AI decision for auditability"""
        try:
            import json
            decision = AIDecision(
                user_id=user_id,
                decision_type=decision_type,
                agent_name="AgentOrchestrator",
                decision_summary=str(decision_data.get("summary", ""))[:500],
                confidence_score=decision_data.get("confidence_score") or decision_data.get("overall_confidence"),
                reasoning=json.dumps(decision_data)[:2000],
                inputs_used={"user_id": user_id},
                outputs_generated=decision_data,
                compliance_check_passed=True,
            )
            db.session.add(decision)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error logging AI decision: {str(e)}")
