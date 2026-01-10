"""
Agent Actions - Execution Layer

Handles persistence and execution of agent decisions.
"""
from datetime import datetime
from ..db import db
from ..models import AgentAction


def create_warning_action(
    user_id: int,
    message: str,
    reasoning: str,
    category: str = None
) -> AgentAction:
    """
    Create a WARNING action
    
    Used when overspending is detected but no immediate intervention needed.
    """
    action = AgentAction(
        user_id=user_id,
        action_type='WARNING',
        message=message,
        reasoning=reasoning,
        category=category,
        resolved=False
    )
    
    db.session.add(action)
    db.session.commit()
    
    return action


def create_budget_adjustment_action(
    user_id: int,
    message: str,
    reasoning: str,
    category: str,
    suggested_budget: float
) -> AgentAction:
    """
    Create a BUDGET_ADJUSTMENT action
    
    Suggests reducing budget for a specific category.
    """
    # Include suggested budget in reasoning
    full_reasoning = f"{reasoning} Suggested budget limit: ₹{suggested_budget:,.2f}"
    
    action = AgentAction(
        user_id=user_id,
        action_type='BUDGET_ADJUSTMENT',
        message=message,
        reasoning=full_reasoning,
        category=category,
        resolved=False,
        action_metadata={'suggested_budget': suggested_budget}
    )
    
    db.session.add(action)
    db.session.commit()
    
    return action


def create_saving_suggestion_action(
    user_id: int,
    message: str,
    reasoning: str,
    suggested_savings: float
) -> AgentAction:
    """
    Create a SAVING_SUGGESTION action
    
    Suggests specific savings amount based on current spending pattern.
    """
    # Include suggested savings in reasoning
    full_reasoning = f"{reasoning} Recommended monthly savings: ₹{suggested_savings:,.2f}"
    
    action = AgentAction(
        user_id=user_id,
        action_type='SAVING_SUGGESTION',
        message=message,
        reasoning=full_reasoning,
        resolved=False,
        action_metadata={'suggested_savings': suggested_savings}
    )
    
    db.session.add(action)
    db.session.commit()
    
    return action


def get_recent_actions(user_id: int, limit: int = 5, unresolved_only: bool = False):
    """
    Get recent agent actions for a user
    
    Args:
        user_id: User ID
        limit: Maximum number of actions to return
        unresolved_only: If True, only return unresolved actions
        
    Returns:
        List of AgentAction objects
    """
    query = AgentAction.query.filter_by(user_id=user_id)
    
    if unresolved_only:
        query = query.filter_by(resolved=False)
    
    return query.order_by(AgentAction.created_at.desc()).limit(limit).all()


def mark_action_resolved(action_id: int, user_id: int) -> bool:
    """
    Mark an agent action as resolved (user acknowledged)
    
    Returns:
        True if action was found and updated, False otherwise
    """
    action = AgentAction.query.filter_by(id=action_id, user_id=user_id).first()
    
    if not action:
        return False
    
    action.resolved = True
    action.resolved_at = datetime.utcnow()
    db.session.commit()
    
    return True
