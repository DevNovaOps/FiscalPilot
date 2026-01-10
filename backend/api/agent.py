"""
Autonomous Financial Agent API endpoints

Provides status and actions from the autonomous agent.
This is NOT a chatbot - agent runs autonomously.
"""
from flask import Blueprint, jsonify
from ..db import db
from ..models import AgentAction
from ..api.auth import get_current_user_id
from ..agent.agent_runner import run_agent_for_user
from ..agent.actions import get_recent_actions, mark_action_resolved

bp = Blueprint('agent', __name__)


@bp.route('/agent/status', methods=['GET'])
def get_agent_status():
    """
    Get autonomous agent status and recent actions
    
    Returns:
        JSON with agent status and recent actions
    """
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    
    try:
        # Get recent unresolved actions
        recent_actions = get_recent_actions(user_id, limit=5, unresolved_only=True)
        
        # Get latest action (resolved or not)
        latest_action = AgentAction.query.filter_by(user_id=user_id)\
            .order_by(AgentAction.created_at.desc()).first()
        
        status = {
            "status": "ACTIVE",
            "unresolved_actions_count": len(recent_actions),
            "recent_actions": [action.to_dict() for action in recent_actions],
            "last_action": latest_action.to_dict() if latest_action else None,
            "last_action_time": latest_action.created_at.isoformat() if latest_action else None,
        }
        
        return jsonify(status), 200
        
    except Exception as e:
        print(f"Error getting agent status: {str(e)}")
        return jsonify({"error": str(e)}), 500


@bp.route('/agent/actions', methods=['GET'])
def get_agent_actions():
    """
    Get all agent actions (with optional filters)
    
    Query params:
        - limit: Number of actions to return (default: 10)
        - unresolved_only: Only return unresolved actions (default: false)
    """
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    
    try:
        from flask import request
        
        limit = request.args.get('limit', 10, type=int)
        unresolved_only = request.args.get('unresolved_only', 'false').lower() == 'true'
        
        actions = get_recent_actions(user_id, limit=limit, unresolved_only=unresolved_only)
        
        return jsonify({
            "actions": [action.to_dict() for action in actions],
            "count": len(actions)
        }), 200
        
    except Exception as e:
        print(f"Error getting agent actions: {str(e)}")
        return jsonify({"error": str(e)}), 500


@bp.route('/agent/actions/<int:action_id>/resolve', methods=['POST'])
def resolve_action(action_id):
    """
    Mark an agent action as resolved (user acknowledged)
    
    This provides feedback to the agent for learning.
    """
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    
    try:
        success = mark_action_resolved(action_id, user_id)
        
        if success:
            return jsonify({"message": "Action marked as resolved"}), 200
        else:
            return jsonify({"error": "Action not found"}), 404
            
    except Exception as e:
        print(f"Error resolving action: {str(e)}")
        return jsonify({"error": str(e)}), 500


@bp.route('/agent/trigger', methods=['POST'])
def trigger_agent():
    """
    Manually trigger agent execution (for testing)
    
    NOTE: Agent runs automatically on sync and dashboard load.
    This endpoint is for manual testing only.
    """
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    
    try:
        result = run_agent_for_user(user_id, force=True)
        
        return jsonify({
            "message": "Agent executed",
            "result": result
        }), 200
        
    except Exception as e:
        print(f"Error triggering agent: {str(e)}")
        return jsonify({"error": str(e)}), 500
