"""
Transactions API routes
"""
from flask import Blueprint, request, jsonify
from ..db import db
from ..models import Transaction
from ..schemas import TransactionCreate
from ..api.auth import get_current_user_id
from datetime import datetime
import csv
import io

bp = Blueprint('transactions', __name__)


@bp.route('', methods=['GET'])
def get_transactions():
    """Get user transactions"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    
    # Query parameters
    days = request.args.get('days', 90, type=int)
    category = request.args.get('category', None)
    
    query = Transaction.query.filter_by(user_id=user_id)
    
    if category:
        query = query.filter_by(category=category)
    
    # Date filter
    from datetime import timedelta
    cutoff_date = datetime.utcnow().date() - timedelta(days=days)
    query = query.filter(Transaction.transaction_date >= cutoff_date)
    
    transactions = query.order_by(Transaction.transaction_date.desc()).all()
    
    return jsonify([t.to_dict() for t in transactions]), 200


@bp.route('', methods=['POST'])
def create_transaction():
    """Create a new transaction"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    
    try:
        data = request.get_json()
        schema = TransactionCreate(**data)
        
        transaction = Transaction(
            user_id=user_id,
            amount=schema.amount,
            description=schema.description,
            transaction_date=schema.transaction_date,
            transaction_type=schema.transaction_type,
            category=schema.category,
            subcategory=schema.subcategory,
            merchant=schema.merchant,
            payment_method=schema.payment_method,
            source=schema.source,
            external_id=schema.external_id
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        return jsonify(transaction.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


@bp.route('/upload-csv', methods=['POST'])
def upload_csv():
    """Upload transactions from CSV file"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    try:
        # Read CSV
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_reader = csv.DictReader(stream)
        
        transactions_created = 0
        errors = []
        
        for row_num, row in enumerate(csv_reader, start=2):
            try:
                # Parse CSV row (adjust based on your CSV format)
                amount = float(row.get('amount', 0))
                description = row.get('description', '') or row.get('description', '')
                date_str = row.get('date', '') or row.get('transaction_date', '')
                
                # Parse date
                try:
                    transaction_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                except:
                    try:
                        transaction_date = datetime.strptime(date_str, '%d/%m/%Y').date()
                    except:
                        transaction_date = datetime.utcnow().date()
                
                transaction_type = row.get('type', 'expense').lower()
                if transaction_type not in ['income', 'expense', 'transfer']:
                    transaction_type = 'expense' if amount < 0 else 'income'
                
                transaction = Transaction(
                    user_id=user_id,
                    amount=amount,
                    description=description or 'Imported transaction',
                    transaction_date=transaction_date,
                    transaction_type=transaction_type,
                    category=row.get('category'),
                    merchant=row.get('merchant'),
                    payment_method=row.get('payment_method'),
                    source='csv'
                )
                
                db.session.add(transaction)
                transactions_created += 1
                
            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)}")
        
        db.session.commit()
        
        return jsonify({
            "message": f"Imported {transactions_created} transactions",
            "transactions_created": transactions_created,
            "errors": errors
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


@bp.route('/<int:transaction_id>', methods=['DELETE'])
def delete_transaction(transaction_id):
    """Delete a transaction"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    
    transaction = Transaction.query.filter_by(id=transaction_id, user_id=user_id).first()
    if not transaction:
        return jsonify({"error": "Transaction not found"}), 404
    
    db.session.delete(transaction)
    db.session.commit()
    
    return jsonify({"message": "Transaction deleted"}), 200
