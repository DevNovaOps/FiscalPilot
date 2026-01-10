"""
User Preferences API routes
"""
from flask import Blueprint, request, jsonify
from ..db import db
from ..models import UserPreference
from ..schemas import UserPreferenceCreate, UserPreferenceResponse
from ..api.auth import get_current_user_id

bp = Blueprint('preferences', __name__)


@bp.route('', methods=['GET'])
def get_preferences():
    """Get user preferences"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    
    prefs = UserPreference.query.filter_by(user_id=user_id).first()
    
    if not prefs:
        return jsonify({"error": "Preferences not found"}), 404
    
    return jsonify(prefs.to_dict()), 200


@bp.route('', methods=['POST', 'PUT'])
def update_preferences():
    """Create or update user preferences"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    
    try:
        data = request.get_json()
        schema = UserPreferenceCreate(**data)
        
        prefs = UserPreference.query.filter_by(user_id=user_id).first()
        
        if prefs:
            # Update existing
            if schema.primary_goal is not None:
                prefs.primary_goal = schema.primary_goal
            if schema.goal_amount is not None:
                prefs.goal_amount = schema.goal_amount
            if schema.goal_timeline_years is not None:
                prefs.goal_timeline_years = schema.goal_timeline_years
            if schema.interested_asset_classes is not None:
                prefs.interested_asset_classes = schema.interested_asset_classes
            if schema.email_notifications is not None:
                prefs.email_notifications = schema.email_notifications
            if schema.insights_frequency is not None:
                prefs.insights_frequency = schema.insights_frequency
        else:
            # Create new
            prefs = UserPreference(
                user_id=user_id,
                primary_goal=schema.primary_goal,
                goal_amount=schema.goal_amount,
                goal_timeline_years=schema.goal_timeline_years,
                interested_asset_classes=schema.interested_asset_classes or [],
                email_notifications=schema.email_notifications if schema.email_notifications is not None else True,
                insights_frequency=schema.insights_frequency or "weekly"
            )
            db.session.add(prefs)
        
        db.session.commit()
        
        return jsonify(prefs.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
