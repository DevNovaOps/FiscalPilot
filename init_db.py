"""
Database initialization script
Creates all tables in the MySQL database
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Ensure UTF-8 encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from backend.app import create_app
from backend.db import db
# Import all models to register them with SQLAlchemy
from backend.models import User, Transaction, RiskProfile, AIDecision, UserPreference, PlaidItem, AgentAction

app = create_app()

with app.app_context():
    print("Creating database tables...")
    try:
        # Create all tables
        db.create_all()
        print("[SUCCESS] Database tables created successfully!")
        print("\nYou can now start the application with: python run.py")
        print("\nTables created:")
        print("  - users")
        print("  - transactions")
        print("  - risk_profiles")
        print("  - ai_decisions")
        print("  - user_preferences")
        print("  - plaid_items")
        print("  - agent_actions")
    except Exception as e:
        print(f"[ERROR] Failed to create database tables: {str(e)}")
        print("\nMake sure:")
        print("  1. MySQL is running")
        print("  2. Database 'fiscal_pilot' exists")
        print("  3. .env file has correct database credentials")
        print("\nTo create the database, run in MySQL:")
        print("  CREATE DATABASE fiscal_pilot CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        sys.exit(1)
