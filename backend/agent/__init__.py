"""
Autonomous Financial Agent Module

This is a rule-based autonomous agent that:
1. Observes user transactions
2. Analyzes spending patterns
3. Plans interventions
4. Takes proactive actions
5. Learns from feedback

This is NOT a chatbot - it operates autonomously without user prompts.
"""
from .agent_runner import run_agent_for_user
from .financial_agent import FinancialAgent

__all__ = ['run_agent_for_user', 'FinancialAgent']
