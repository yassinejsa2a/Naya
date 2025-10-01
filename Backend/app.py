#!/usr/bin/env python3
"""
NAYA Travel Journal - Main Flask Application
"""
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import Config
from models import db, User, Place, Review, Photo
from api.auth import auth_bp
from api.reviews import reviews_bp
from api.photos import photos_bp
from api.places import places_bp

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    jwt = JWTManager(app)
    CORS(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(reviews_bp, url_prefix='/api')
    app.register_blueprint(photos_bp, url_prefix='/api')
    app.register_blueprint(places_bp, url_prefix='/api')
    
    @app.route('/')
    def home():
        """Home endpoint"""
        return jsonify({
            "message": "Welcome to NAYA Travel Journal API",
            "version": "1.0.0",
            "endpoints": {
                "auth": "/api/register, /api/login",
                "reviews": "/api/reviews",
                "photos": "/api/photos",
                "places": "/api/places"
            }
        })
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors"""
        return jsonify({"error": "Not found"}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors"""
        return jsonify({"error": "Internal server error"}), 500
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)