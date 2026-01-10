"""
Plaid API routes for bank account integration
NOTE: This uses Plaid sandbox (demo only), not RBI Account Aggregator.

SECURITY RULES:
- Never expose PLAID_SECRET to frontend
- Never store bank credentials
- Access token stored server-side only
- Use sandbox banks only
"""
from flask import Blueprint, request, jsonify
from datetime import datetime
from ..db import db
from ..models import PlaidItem, Transaction
from ..api.auth import get_current_user_id
from ..plaid_client import (
    create_link_token,
    exchange_public_token,
    get_institution_name,
    fetch_transactions
)

bp = Blueprint('plaid', __name__)


@bp.route('/plaid/create-link-token', methods=['POST'])
def create_link_token_endpoint():
    """
    Create a Plaid Link token for frontend
    
    Returns:
        JSON with link_token for Plaid Link frontend component
        
    SECURITY: No sensitive data returned, only temporary link_token
    """
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    
    try:
        link_token = create_link_token(user_id, "Fiscal Pilot")
        return jsonify({"link_token": link_token}), 200
    except Exception as e:
        print(f"Error creating link token: {str(e)}")
        return jsonify({"error": f"Failed to create link token: {str(e)}"}), 500


@bp.route('/plaid/exchange-public-token', methods=['POST'])
def exchange_public_token_endpoint():
    """
    Exchange public_token for access_token and store in database
    
    SECURITY: 
    - Receives public_token from frontend (one-time use, safe)
    - Exchanges for access_token server-side
    - Stores access_token in database (never sent to frontend)
    
    Request body:
        {
            "public_token": "public-sandbox-xxx",
            "metadata": { ... }  // Optional Plaid Link metadata
        }
    """
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    
    try:
        data = request.get_json()
        public_token = data.get('public_token')
        
        if not public_token:
            return jsonify({"error": "public_token is required"}), 400
        
        # Exchange public_token for access_token (server-side only)
        exchange_result = exchange_public_token(public_token)
        access_token = exchange_result['access_token']
        item_id = exchange_result['item_id']
        
        # Get institution name
        institution_name = get_institution_name(access_token)
        
        # Check if item already exists (user might reconnect)
        existing_item = PlaidItem.query.filter_by(item_id=item_id).first()
        
        if existing_item:
            # Update existing item
            existing_item.access_token = access_token
            existing_item.institution_name = institution_name
            existing_item.is_active = True
            existing_item.updated_at = datetime.utcnow()
            db.session.commit()
            
            return jsonify({
                "message": "Bank account reconnected successfully",
                "item_id": item_id,
                "institution_name": institution_name
            }), 200
        else:
            # Create new PlaidItem
            plaid_item = PlaidItem(
                user_id=user_id,
                access_token=access_token,  # Stored server-side only
                item_id=item_id,
                institution_name=institution_name,
                is_active=True
            )
            
            db.session.add(plaid_item)
            db.session.commit()
            
            # Immediately sync transactions after connection
            try:
                sync_transactions_for_user(user_id)
            except Exception as sync_error:
                print(f"Error during initial sync: {str(sync_error)}")
                # Continue even if sync fails, user can sync manually later
            
            return jsonify({
                "message": "Bank account connected successfully",
                "item_id": item_id,
                "institution_name": institution_name
            }), 201
            
    except Exception as e:
        db.session.rollback()
        print(f"Error exchanging public token: {str(e)}")
        return jsonify({"error": f"Failed to connect bank account: {str(e)}"}), 500


@bp.route('/plaid/sync-transactions', methods=['GET'])
def sync_transactions_endpoint():
    """
    Sync transactions from all connected bank accounts
    
    Returns:
        JSON with sync results (count of new transactions)
        
    SECURITY: Uses server-side stored access_tokens only
    """
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    
    try:
        result = sync_transactions_for_user(user_id)
        return jsonify(result), 200
    except Exception as e:
        print(f"Error syncing transactions: {str(e)}")
        return jsonify({"error": f"Failed to sync transactions: {str(e)}"}), 500


def sync_transactions_for_user(user_id: int) -> dict:
    """
    Sync transactions for a user from all their connected Plaid items
    
    SECURITY: All access_tokens retrieved from database (server-side only)
    
    Automatically triggers autonomous financial agent after sync completes.
    
    Args:
        user_id: User ID to sync transactions for
        
    Returns:
        dict with sync statistics
    """
    # Get all active Plaid items for user
    plaid_items = PlaidItem.query.filter_by(
        user_id=user_id,
        is_active=True
    ).all()
    
    if not plaid_items:
        return {
            "message": "No bank accounts connected",
            "transactions_added": 0,
            "transactions_skipped": 0
        }
    
    total_added = 0
    total_skipped = 0
    
    for plaid_item in plaid_items:
        try:
            # Fetch transactions from Plaid (using server-side access_token)
            plaid_transactions = fetch_transactions(plaid_item.access_token, days=30)
            
            added, skipped = save_transactions_from_plaid(
                user_id=user_id,
                plaid_transactions=plaid_transactions,
                institution_name=plaid_item.institution_name
            )
            
            total_added += added
            total_skipped += skipped
            
        except Exception as e:
            print(f"Error syncing transactions for item {plaid_item.item_id}: {str(e)}")
            # Continue with other items even if one fails
            continue
    
    # Trigger autonomous financial agent after sync (if new transactions added)
    if total_added > 0:
        try:
            from ..agent.agent_runner import run_agent_for_user
            agent_result = run_agent_for_user(user_id)
            print(f"Agent executed after sync: {agent_result.get('actions_taken', 0)} actions taken")
        except Exception as e:
            print(f"Error running agent after sync: {str(e)}")
            # Don't fail sync if agent fails
    
    return {
        "message": "Transactions synced successfully",
        "transactions_added": total_added,
        "transactions_skipped": total_skipped
    }


def save_transactions_from_plaid(user_id: int, plaid_transactions: list, institution_name: str) -> tuple:
    """
    Parse and save Plaid transactions to database
    
    Business Logic:
    - amount > 0 → Expense (outflow)
    - amount < 0 → Income (inflow) [some Plaid accounts show income as negative]
    
    Args:
        user_id: User ID
        plaid_transactions: List of transaction dicts from Plaid API
        institution_name: Bank name for reference
        
    Returns:
        tuple (added_count, skipped_count)
    """
    added = 0
    skipped = 0
    
    for plaid_tx in plaid_transactions:
        try:
            # Get transaction ID (UNIQUE constraint prevents duplicates)
            # Handle both object and dict response from Plaid API
            if hasattr(plaid_tx, 'transaction_id'):
                transaction_id = plaid_tx.transaction_id
            else:
                transaction_id = plaid_tx.get('transaction_id')
            
            if not transaction_id:
                print(f"Skipping transaction without ID: {plaid_tx}")
                skipped += 1
                continue
            
            # Convert to string for database storage
            transaction_id = str(transaction_id)
            
            # Check if transaction already exists (by transaction_id)
            existing = Transaction.query.filter_by(transaction_id=transaction_id).first()
            if existing:
                skipped += 1
                continue
            
            # Parse amount (handle both object and dict)
            if hasattr(plaid_tx, 'amount'):
                amount = float(plaid_tx.amount)
                # Get date
                transaction_date_obj = plaid_tx.date if hasattr(plaid_tx, 'date') else None
                if transaction_date_obj:
                    if hasattr(transaction_date_obj, 'strftime'):
                        transaction_date_str = transaction_date_obj.strftime('%Y-%m-%d')
                    else:
                        transaction_date_str = str(transaction_date_obj)
                else:
                    transaction_date_str = None
                # Get category
                plaid_category = plaid_tx.category if hasattr(plaid_tx, 'category') else None
                # Get merchant/name
                merchant = plaid_tx.merchant_name if hasattr(plaid_tx, 'merchant_name') else (plaid_tx.name if hasattr(plaid_tx, 'name') else '')
                transaction_name = plaid_tx.name if hasattr(plaid_tx, 'name') else 'Transaction'
            else:
                # Fallback to dict access
                amount = float(plaid_tx.get('amount', 0))
                transaction_date_str = plaid_tx.get('date')
                plaid_category = plaid_tx.get('category')
                merchant = plaid_tx.get('merchant_name') or plaid_tx.get('name', '')
                transaction_name = plaid_tx.get('name', 'Transaction')
            
            # Determine transaction type based on amount
            # Plaid: positive amount = outflow (expense), negative = inflow (income)
            # Our system: positive = income, negative = expense
            if amount > 0:
                # Positive amount in Plaid = expense (outflow)
                transaction_type = 'expense'
                # Keep as negative for our system
                amount = -abs(amount)
            else:
                # Negative amount in Plaid = income (inflow)
                transaction_type = 'income'
                # Convert to positive for our system
                amount = abs(amount)
            
            # Parse date
            try:
                if transaction_date_str:
                    transaction_date = datetime.strptime(str(transaction_date_str), '%Y-%m-%d').date()
                else:
                    transaction_date = datetime.utcnow().date()
            except:
                transaction_date = datetime.utcnow().date()
            
            # Get category from Plaid (auto-assign)
            category = None
            if plaid_category:
                if isinstance(plaid_category, list) and len(plaid_category) > 0:
                    # Use primary category (first in list)
                    category = plaid_category[0] if isinstance(plaid_category[0], str) else str(plaid_category[0])
                elif isinstance(plaid_category, str):
                    category = plaid_category
            
            # Get payment method
            if hasattr(plaid_tx, 'payment_channel'):
                payment_method = plaid_tx.payment_channel
            else:
                payment_method = plaid_tx.get('payment_channel', 'bank_transfer')
            
            # Create transaction
            transaction = Transaction(
                user_id=user_id,
                amount=amount,
                description=transaction_name,
                transaction_date=transaction_date,
                transaction_type=transaction_type,
                category=category,
                merchant=merchant if merchant else None,
                payment_method=payment_method,
                transaction_id=transaction_id,  # UNIQUE constraint prevents duplicates
                source='plaid',  # Mark as from Plaid
                external_id=transaction_id
            )
            
            db.session.add(transaction)
            added += 1
            
        except Exception as e:
            print(f"Error processing Plaid transaction: {str(e)}")
            skipped += 1
            continue
    
    # Commit all transactions at once
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error committing transactions: {str(e)}")
        raise
    
    return (added, skipped)


@bp.route('/plaid/status', methods=['GET'])
def get_plaid_status():
    """
    Get status of connected bank accounts
    
    Returns:
        JSON with list of connected accounts
    """
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    
    plaid_items = PlaidItem.query.filter_by(user_id=user_id, is_active=True).all()
    
    return jsonify({
        "connected_accounts": [item.to_dict() for item in plaid_items],
        "count": len(plaid_items)
    }), 200
