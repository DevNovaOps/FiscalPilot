"""
Authentication API routes
"""
from flask import Blueprint, request, jsonify, session
from ..db import db
from ..models import User
from ..schemas import UserCreate, UserLogin
import jwt
from datetime import datetime, timedelta
from ..config import settings

bp = Blueprint('auth', __name__)


def generate_token(user_id: int) -> str:
    """Generate JWT token for user"""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=7),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')


def get_current_user_id():
    """Get current user ID from token"""
    token = request.headers.get('Authorization')
    if not token or not token.startswith('Bearer '):
        return None
    
    try:
        token = token.split(' ')[1]
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        return payload.get('user_id')
    except:
        return None


@bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        schema = UserCreate(**data)
        
        # Check if user exists
        existing_user = User.query.filter_by(email=schema.email).first()
        if existing_user:
            return jsonify({"error": "User already exists"}), 400
        
        # Create user
        user = User(
            email=schema.email,
            full_name=schema.full_name,
            data_consent=schema.data_consent,
            consent_date=datetime.utcnow() if schema.data_consent else None,
            consent_version="1.0"
        )
        user.set_password(schema.password)
        
        db.session.add(user)
        db.session.commit()
        
        token = generate_token(user.id)
        
        return jsonify({
            "message": "User created successfully",
            "user": user.to_dict(),
            "token": token
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


@bp.route('/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.get_json()
        schema = UserLogin(**data)
        
        user = User.query.filter_by(email=schema.email).first()
        if not user or not user.check_password(schema.password):
            return jsonify({"error": "Invalid credentials"}), 401
        
        token = generate_token(user.id)
        
        return jsonify({
            "message": "Login successful",
            "user": user.to_dict(),
            "token": token
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@bp.route('/me', methods=['GET'])
def get_current_user():
    """Get current user information"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    return jsonify(user.to_dict()), 200
