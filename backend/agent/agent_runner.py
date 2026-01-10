"""
Agent Runner - Triggers autonomous agent execution

Runs automatically on:
- Dashboard load
- After Plaid transaction sync
- Periodically (optional)

This is NOT a chatbot - agent runs autonomously without user prompts.
"""
from .financial_agent import FinancialAgent


def run_agent_for_user(user_id: int, force: bool = False) -> dict:
    """
    Run the autonomous financial agent for a user
    
    This executes the full OBSERVE → ANALYZE → PLAN → ACT cycle
    
    Args:
        user_id: User ID to run agent for
        force: If True, run even if recently run (default: False - respects cooldown)
        
    Returns:
        Dict with agent execution results
    """
    try:
        # Create agent instance
        agent = FinancialAgent(user_id=user_id)
        
        # Run full cycle
        result = agent.run_full_cycle()
        
        return result
        
    except Exception as e:
        print(f"Error running agent for user {user_id}: {str(e)}")
        return {
            'status': 'error',
            'message': str(e),
            'actions_taken': 0
        }


def should_run_agent(user_id: int) -> bool:
    """
    Determine if agent should run (cooldown logic)
    
    Returns True if agent should run, False if it should wait
    Currently returns True always - can be enhanced with cooldown logic
    """
    # TODO: Add cooldown logic (e.g., don't run if ran in last 5 minutes)
    # For now, always return True to run on every trigger
    return True
