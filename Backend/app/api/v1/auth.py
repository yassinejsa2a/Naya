#!/usr/bin/env python3
"""
Authentication API endpoints
"""

# Routes auth pour inscription/connexion/profils.

import os

from flask import Blueprint, request, jsonify, current_app, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from app.services.auth import AuthService

auth_bp = Blueprint('auth', __name__)
auth_service = AuthService()

@auth_bp.route('/register', methods=['POST'])
# Inscrit un nouvel utilisateur.
def register():
    """Register new user"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        result = auth_service.register_user(data)
        return jsonify(result), 201
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Registration failed"}), 500

@auth_bp.route('/login', methods=['POST'])
# Authentifie via email/pseudo + mot de passe.
def login():
    """User login"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        login_value = (data.get('email') or data.get('username') or data.get('login'))
        password = data.get('password')
        
        if not login_value or not password:
            return jsonify({"error": "Login (email or username) and password are required"}), 400
        
        result = auth_service.authenticate_user(login_value, password)
        return jsonify(result), 200
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 401
    except Exception as e:
        return jsonify({"error": "Login failed"}), 500

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
# Renvoie le profil connecté.
def get_profile():
    """Get user profile"""
    try:
        current_user_id = get_jwt_identity()
        result = auth_service.get_user_profile(current_user_id)
        return jsonify(result), 200
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "Failed to get profile"}), 500

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
# Met à jour le profil.
def update_profile():
    """Update user profile"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        result = auth_service.update_user_profile(current_user_id, data)
        return jsonify(result), 200
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Failed to update profile"}), 500

@auth_bp.route('/change-password', methods=['PUT'])
@jwt_required()
# Change le mot de passe.
def change_password():
    """Change user password"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        
        if not old_password or not new_password:
            return jsonify({"error": "Both old and new passwords are required"}), 400
        
        result = auth_service.change_password(current_user_id, old_password, new_password)
        return jsonify(result), 200
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Failed to change password"}), 500

@auth_bp.route('/avatar', methods=['PUT'])
@jwt_required()
# Téléverse un avatar.
def update_avatar():
    """Upload or replace the authenticated user's profile photo."""
    try:
        current_user_id = get_jwt_identity()
        file_storage = (
            request.files.get('avatar')
            or request.files.get('file')
            or (next(iter(request.files.values())) if request.files else None)
        )

        if not file_storage:
            return jsonify({"error": "No file provided"}), 400

        result = auth_service.update_profile_photo(current_user_id, file_storage)
        return jsonify(result), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception:
        current_app.logger.exception('Failed to update avatar')
        return jsonify({"error": "Failed to update profile photo"}), 500

@auth_bp.route('/avatar/<path:filename>', methods=['GET'])
# Sert un avatar depuis le disque.
def serve_avatar(filename):
    """Serve stored profile photos."""
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    if os.path.isabs(upload_folder):
        directory = os.path.join(upload_folder, 'avatars')
    else:
        directory = os.path.join(current_app.root_path, upload_folder, 'avatars')
    return send_from_directory(directory, filename)

@auth_bp.route('/deactivate', methods=['PUT'])
@jwt_required()
# Désactive l'utilisateur courant.
def deactivate_account():
    """Deactivate user account"""
    try:
        current_user_id = get_jwt_identity()
        result = auth_service.deactivate_user(current_user_id)
        return jsonify(result), 200
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "Failed to deactivate account"}), 500

@auth_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_user_stats():
    """Get user statistics"""
    try:
        current_user_id = get_jwt_identity()
        result = auth_service.get_user_stats(current_user_id)
        return jsonify(result), 200
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "Failed to get user stats"}), 500


@auth_bp.route('/users/<user_id>', methods=['GET'])
def public_profile(user_id):
    """Get public profile information for a given user."""
    try:
        profile = auth_service.get_public_profile(user_id)
        return jsonify({'user': profile}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception:
        current_app.logger.exception('Failed to load public profile')
        return jsonify({'error': 'Failed to load profile'}), 500


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_token():
    """Issue a new access token using a refresh token."""
    identity = get_jwt_identity()
    new_access_token = create_access_token(identity=identity)
    return jsonify({'access_token': new_access_token}), 200

@auth_bp.errorhandler(400)
def bad_request(error):
    return jsonify({"error": "Bad request"}), 400

@auth_bp.errorhandler(401)
def unauthorized(error):
    return jsonify({"error": "Unauthorized"}), 401

@auth_bp.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404

@auth_bp.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500
