"""
Analysis API routes - AI agent orchestration
"""
from flask import Blueprint, request, jsonify
from ..agents import AgentOrchestrator
from ..api.auth import get_current_user_id
from ..models import RiskProfile, AIDecision

bp = Blueprint('analysis', __name__)
orchestrator = AgentOrchestrator()

@bp.route('/full-analysis', methods=['POST'])
def full_analysis():
    """Run complete AI analysis for user"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    
    try:
        # Run orchestration
        result = orchestrator.run(user_id)
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route('/risk-profile', methods=['GET'])
def get_risk_profile():
    """Get user's current risk profile"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    
    risk_profile = RiskProfile.query.filter_by(user_id=user_id).first()
    
    if not risk_profile:
        # Trigger analysis if no profile exists
        try:
            result = orchestrator.run(user_id)
            risk_profile = RiskProfile.query.filter_by(user_id=user_id).first()
        except:
            pass
    
    if not risk_profile:
        return jsonify({"error": "Risk profile not available"}), 404
    
    return jsonify(risk_profile.to_dict()), 200


@bp.route('/insights', methods=['GET'])
def get_insights():
    """Get AI insights and explanations"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    
    # Get recent decisions
    decisions = AIDecision.query.filter_by(
        user_id=user_id
    ).order_by(AIDecision.created_at.desc()).limit(10).all()
    
    return jsonify([d.to_dict() for d in decisions]), 200
