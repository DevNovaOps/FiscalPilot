"""
Multi-Agent Investment Advisory System

This module implements a path-based, multi-agent investment advisory system.
Agents communicate via structured JSON messages and route users through
dynamic investment paths based on their financial profile.
"""
from .orchestrator import InvestmentOrchestrator
from .profiler_agent import ProfilerAgent
from .intent_agent import IntentAgent
from .router_agent import RouterAgent
from .equity_agent import EquityAgent
from .etf_agent import ETFAgent
from .risk_agent import RiskAgent
from .consensus_agent import ConsensusAgent

__all__ = [
    "InvestmentOrchestrator",
    "ProfilerAgent",
    "IntentAgent",
    "RouterAgent",
    "EquityAgent",
    "ETFAgent",
    "RiskAgent",
    "ConsensusAgent",
]