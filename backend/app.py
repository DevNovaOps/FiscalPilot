"""
Fiscal Pilot Flask Application
Main entry point for the backend
"""
import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import database and models
from .db import db
from .config import settings, DATABASE_URI
from .models import User, Transaction, AIDecision, UserPreference, RiskProfile

# Import API routes
from .api import auth, transactions, analysis, preferences, mock


def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__, 
                static_folder='../frontend',
                static_url_path='',
                template_folder='../frontend')
    
    # Configuration
    app.config['SECRET_KEY'] = settings.SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['MAX_CONTENT_LENGTH'] = settings.MAX_CONTENT_LENGTH
    app.config['UPLOAD_FOLDER'] = settings.UPLOAD_FOLDER
    
    # Initialize extensions
    db.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})  # Allow API access from frontend
    
    # Register blueprints
    app.register_blueprint(auth.bp, url_prefix='/api/auth')
    app.register_blueprint(transactions.bp, url_prefix='/api/transactions')
    app.register_blueprint(analysis.bp, url_prefix='/api/analysis')
    app.register_blueprint(preferences.bp, url_prefix='/api/preferences')
    app.register_blueprint(mock.bp, url_prefix='/api')
    
    # Serve frontend files
    @app.route('/')
    def index():
        return send_from_directory(app.static_folder, 'index.html')
    
    @app.route('/<path:path>')
    def serve_static(path):
        """Serve static files from frontend directory"""
        return send_from_directory(app.static_folder, path)
    
    # Note: Database tables are created by init_db.py
    # Don't create them here to avoid connection errors on import
    # with app.app_context():
    #     db.create_all()
    
    return app


# Create app instance
app = create_app()


if __name__ == '__main__':
    port = settings.PORT
    debug = settings.DEBUG
    
    print(f"""
    ╔══════════════════════════════════════╗
    ║   FISCAL PILOT - Starting Server     ║
    ╚══════════════════════════════════════╝
    
    Server running on: http://localhost:{port}
    Environment: {'Development' if debug else 'Production'}
    Database: {settings.DB_NAME}
    
    """)
    
    app.run(host='0.0.0.0', port=port, debug=debug)
