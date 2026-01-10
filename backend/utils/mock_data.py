"""
Mock Account Aggregator data generator
For demonstration and testing purposes
"""
from typing import List, Dict, Any
from datetime import datetime, timedelta
import random


def generate_mock_transactions(count: int = 30) -> List[Dict[str, Any]]:
    """
    Generate mock transaction data
    Simulates Account Aggregator format
    
    Args:
        count: Number of transactions to generate
        
    Returns:
        List of mock transaction dictionaries
    """
    categories = [
        "Food & Dining", "Transportation", "Shopping", 
        "Bills & Utilities", "Entertainment", "Healthcare",
        "Salary/Income", "EMI", "Subscriptions"
    ]
    
    merchants = [
        "Amazon", "Flipkart", "Swiggy", "Zomato", "Uber", "Ola",
        "Netflix", "Spotify", "PhonePe", "GPay", "Salary Account",
        "Electricity Board", "Water Works", "Grocery Store"
    ]
    
    transactions = []
    today = datetime.now().date()
    
    # Add a salary transaction
    transactions.append({
        "amount": 50000.00,
        "description": "Monthly Salary",
        "transaction_date": (today.replace(day=1) - timedelta(days=1)).isoformat(),
        "transaction_type": "income",
        "category": "Salary/Income",
        "merchant": "Salary Account",
        "payment_method": "bank_transfer",
        "source": "mock_aa"
    })
    
    # Generate random expenses
    for i in range(count - 1):
        days_ago = random.randint(0, 90)
        date = (today - timedelta(days=days_ago)).isoformat()
        
        category = random.choice(categories)
        merchant = random.choice(merchants)
        
        # Determine amount based on category
        if category == "Salary/Income":
            amount = random.uniform(30000, 80000)
            tx_type = "income"
        elif category == "EMI":
            amount = -random.uniform(5000, 15000)
            tx_type = "expense"
        elif category == "Subscriptions":
            amount = -random.uniform(200, 1000)
            tx_type = "expense"
        elif category == "Food & Dining":
            amount = -random.uniform(200, 2000)
            tx_type = "expense"
        elif category == "Transportation":
            amount = -random.uniform(50, 500)
            tx_type = "expense"
        else:
            amount = -random.uniform(100, 5000)
            tx_type = "expense"
        
        transactions.append({
            "amount": round(amount, 2),
            "description": f"{merchant} Payment",
            "transaction_date": date,
            "transaction_type": tx_type,
            "category": category,
            "merchant": merchant,
            "payment_method": random.choice(["credit_card", "debit_card", "upi", "cash"]),
            "source": "mock_aa",
            "external_id": f"MOCK_{random.randint(100000, 999999)}"
        })
    
    # Sort by date (newest first)
    transactions.sort(key=lambda x: x["transaction_date"], reverse=True)
    
    return transactions


def get_mock_aa_consent_explanation() -> str:
    """Get explanation of mock Account Aggregator consent"""
    return """
    **Mock Account Aggregator Data**
    
    In this demo, we're using simulated transaction data that mimics what 
    you would receive from an Account Aggregator (AA) framework.
    
    **In Production:**
    - Real Account Aggregator integration would require user consent via AA framework
    - Data would be fetched securely from your bank accounts
    - All data transfer would be encrypted and compliant with regulations
    
    **Current Implementation:**
    - Mock data is generated for demonstration
    - You can also upload CSV files with your transaction data
    - All data is stored securely in your database
    
    **Privacy:**
    - Your data is never shared with third parties
    - All AI analysis happens on your data
    - You can delete your data at any time
    """
