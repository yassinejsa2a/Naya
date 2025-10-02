#!/usr/bin/env python3
"""
NAYA Travel Journal - Flask Application
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS

# Initialize extensions
db = SQLAlchemy()
jwt = JWTManager()

def create_app(config_object='config.Config'):
    """Create Flask application"""
    app = Flask(__name__)
    
    # Load configuration
    from config import get_config
    config_class = get_config()
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    CORS(app)
    
    # Register API routes
    from app.api.v1 import api_v1
    app.register_blueprint(api_v1)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    @app.route('/')
    def home():
        return {
            "message": "NAYA Travel Journal API",
            "version": "1.0.0",
            "status": "running"
        }
    
    @app.errorhandler(404)
    def not_found(error):
        return {"error": "Not found"}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return {"error": "Internal server error"}, 500
    
    return app