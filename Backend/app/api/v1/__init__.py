#!/usr/bin/env python3
"""
API v1 package initialization
"""

from flask import Blueprint

def create_v1_blueprint():
    """Create and configure the API v1 blueprint with all routes"""
    # Create main v1 blueprint
    v1_bp = Blueprint('v1', __name__, url_prefix='/api/v1')
    
    # Import and register auth routes
    from .auth import auth_bp
    v1_bp.register_blueprint(auth_bp, url_prefix='/auth')
    
    # Import and register places routes
    from .places import places_bp
    v1_bp.register_blueprint(places_bp, url_prefix='/places')
    
    # Import and register reviews routes
    from .reviews import reviews_bp
    v1_bp.register_blueprint(reviews_bp, url_prefix='/reviews')
    
    # Import and register photos routes
    from .photos import photos_bp
    v1_bp.register_blueprint(photos_bp, url_prefix='/photos')
    
    return v1_bp

# Create the blueprint instance
api_v1 = create_v1_blueprint()