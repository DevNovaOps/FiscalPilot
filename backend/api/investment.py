"""
Investment Advisor API endpoints

Provides endpoints for the multi-agent investment advisory system.
This is NOT a chatbot - agents analyze user data autonomously.
"""
from flask import Blueprint, jsonify, request
from ..db import db
from ..models import InvestmentRecommendation
from ..api.auth import get_current_user_id
from ..agents.investment import InvestmentOrchestrator

bp = Blueprint('investment', __name__)

orchestrator = InvestmentOrchestrator()


@bp.route('/investment/recommendation', methods=['GET', 'POST'])
def get_or_generate_recommendation():
    """
    Get or generate investment recommendation
    
    GET: Returns latest recommendation if available
    POST: Forces regeneration of recommendation
    """
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    
    try:
        if request.method == 'POST':
            # Generate new recommendation
            result = orchestrator.generate_recommendation(user_id)
            
            if result["status"] == "error":
                return jsonify({
                    "error": result.get("message", "Failed to generate recommendation")
                }), 500
            
            return jsonify({
                "status": "success",
                "recommendation": result["recommendation"],
                "message": "Investment recommendation generated successfully"
            }), 200
        else:
            # GET: Return latest recommendation
            recommendation = orchestrator.get_latest_recommendation(user_id)
            
            if not recommendation:
                return jsonify({
                    "status": "not_found",
                    "message": "No recommendation found. Use POST to generate one.",
                    "recommendation": None
                }), 404
            
            return jsonify({
                "status": "success",
                "recommendation": recommendation.to_dict(),
                "message": "Latest investment recommendation"
            }), 200
            
    except Exception as e:
        print(f"Error in investment recommendation endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500


@bp.route('/investment/recommendation/latest', methods=['GET'])
def get_latest_recommendation():
    """Get latest investment recommendation"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    
    try:
        recommendation = orchestrator.get_latest_recommendation(user_id)
        
        if not recommendation:
            return jsonify({
                "status": "not_found",
                "message": "No recommendation found",
                "recommendation": None
            }), 404
        
        return jsonify({
            "status": "success",
            "recommendation": recommendation.to_dict()
        }), 200
        
    except Exception as e:
        print(f"Error getting latest recommendation: {str(e)}")
        return jsonify({"error": str(e)}), 500


@bp.route('/investment/recommendation/history', methods=['GET'])
def get_recommendation_history():
    """Get history of investment recommendations"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    
    try:
        from flask import request
        
        limit = request.args.get('limit', 10, type=int)
        
        recommendations = InvestmentRecommendation.query.filter_by(user_id=user_id)\
            .order_by(InvestmentRecommendation.created_at.desc())\
            .limit(limit)\
            .all()
        
        return jsonify({
            "status": "success",
            "recommendations": [rec.to_dict() for rec in recommendations],
            "count": len(recommendations)
        }), 200
        
    except Exception as e:
        print(f"Error getting recommendation history: {str(e)}")
        return jsonify({"error": str(e)}), 500