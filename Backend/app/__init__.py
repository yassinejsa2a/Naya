#!/usr/bin/env python3
"""
NAYA Travel Journal - Flask Application
"""

import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from sqlalchemy import inspect, text

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
    _apply_environment_overrides(app)
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Register API routes
    from app.api.v1 import api_v1
    app.register_blueprint(api_v1)
    
    # Create database tables
    with app.app_context():
        db.create_all()
        _ensure_schema_integrity()
        _ensure_default_admin(app)
    
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


def _ensure_schema_integrity():
    """Ensure runtime schema matches latest model requirements."""
    inspector = inspect(db.engine)
    review_columns = {column['name'] for column in inspector.get_columns('reviews')}
    if 'visit_date' not in review_columns:
        with db.engine.begin() as connection:
            connection.execute(text('ALTER TABLE reviews ADD COLUMN visit_date DATE'))

    user_columns = {column['name'] for column in inspector.get_columns('users')}
    if 'is_admin' not in user_columns:
        with db.engine.begin() as connection:
            connection.execute(text('ALTER TABLE users ADD COLUMN is_admin BOOLEAN NOT NULL DEFAULT 0'))


def _apply_environment_overrides(app):
    """Refresh configuration settings that depend on environment variables."""
    raw_admin_emails = os.getenv('ADMIN_EMAILS')
    if raw_admin_emails is not None:
        admin_emails = [email.strip().lower() for email in raw_admin_emails.split(',') if email.strip()]
    else:
        configured = app.config.get('ADMIN_EMAILS', []) or []
        admin_emails = [email.strip().lower() for email in configured if email]

    default_email = os.getenv('ADMIN_DEFAULT_EMAIL', app.config.get('ADMIN_DEFAULT_EMAIL', '')).strip().lower()
    if default_email and default_email not in admin_emails:
        admin_emails.append(default_email)

    default_password = os.getenv('ADMIN_DEFAULT_PASSWORD', app.config.get('ADMIN_DEFAULT_PASSWORD', ''))

    app.config['ADMIN_EMAILS'] = admin_emails
    app.config['ADMIN_DEFAULT_EMAIL'] = default_email
    app.config['ADMIN_DEFAULT_PASSWORD'] = default_password


def _ensure_default_admin(app):
    """Provision a default admin account if configured."""
    admin_email = (app.config.get('ADMIN_DEFAULT_EMAIL') or '').strip().lower()
    admin_password = app.config.get('ADMIN_DEFAULT_PASSWORD') or ''
    admin_emails = app.config.get('ADMIN_EMAILS', [])

    if not admin_email and admin_emails:
        admin_email = admin_emails[0]

    if not admin_email:
        return

    from app.models.user import User

    existing = User.query.filter_by(email=admin_email).first()
    if existing:
        changed = False
        if not existing.is_admin:
            existing.is_admin = True
            changed = True
        if admin_password:
            try:
                existing.set_password(admin_password)
                changed = True
            except ValueError:
                app.logger.warning('Provided ADMIN_DEFAULT_PASSWORD is invalid; skipping password update')
        if changed:
            db.session.commit()
            app.logger.info('Updated admin account %s', admin_email)
        return

    if not admin_password:
        app.logger.warning('ADMIN_DEFAULT_PASSWORD missing; cannot create default admin account for %s', admin_email)
        return

    base_username = admin_email.split('@')[0] or 'admin'
    username = base_username
    suffix = 1
    while User.query.filter_by(username=username).first():
        username = f"{base_username}{suffix}"
        suffix += 1

    user = User(
        username=username,
        email=admin_email,
        is_admin=True,
        is_active=True,
        is_verified=True,
    )
    try:
        user.set_password(admin_password)
    except ValueError:
        app.logger.warning('Provided ADMIN_DEFAULT_PASSWORD is invalid; skipping default admin provisioning')
        return

    db.session.add(user)
    db.session.commit()
    app.logger.info('Provisioned default admin account %s', admin_email)
