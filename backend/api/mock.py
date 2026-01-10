"""
Mock Account Aggregator API endpoint
For demonstration purposes
"""
from flask import Blueprint, jsonify, request
from ..utils.mock_data import generate_mock_transactions, get_mock_aa_consent_explanation
from ..api.auth import get_current_user_id
from ..schemas.transaction import TransactionCreate
from ..db import db
from ..models.transaction import Transaction
from datetime import datetime

bp = Blueprint('mock', __name__)


@bp.route('/mock-aa/consent', methods=['GET'])
def get_consent_info():
    """Get information about mock Account Aggregator consent"""
    from ..utils.mock_data import get_mock_aa_consent_explanation
    return jsonify({
        "explanation": get_mock_aa_consent_explanation(),
        "note": "This is a mock implementation for demonstration purposes."
    }), 200


@bp.route('/mock-aa/import', methods=['POST'])
def import_mock_data():
    """Import mock Account Aggregator transaction data"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    
    try:
        # Get count from request or use default
        count = 30
        data = request.get_json() or {}
        if 'count' in data:
            count = min(max(1, int(data['count'])), 100)  # Limit between 1-100
        
        # Generate mock transactions
        mock_transactions = generate_mock_transactions(count)
        
        # Import transactions
        imported = 0
        for tx_data in mock_transactions:
            try:
                transaction = Transaction(
                    user_id=user_id,
                    amount=tx_data['amount'],
                    description=tx_data['description'],
                    transaction_date=datetime.fromisoformat(tx_data['transaction_date']).date(),
                    transaction_type=tx_data['transaction_type'],
                    category=tx_data.get('category'),
                    merchant=tx_data.get('merchant'),
                    payment_method=tx_data.get('payment_method'),
                    source='mock_aa',
                    external_id=tx_data.get('external_id')
                )
                db.session.add(transaction)
                imported += 1
            except Exception as e:
                continue
        
        db.session.commit()
        
        return jsonify({
            "message": f"Successfully imported {imported} mock transactions",
            "transactions_imported": imported,
            "source": "mock_aa"
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
