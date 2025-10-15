#!/usr/bin/env python3
"""
Photos API endpoints
"""

import os

from flask import Blueprint, request, jsonify, current_app, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.photo_service import PhotoService

photos_bp = Blueprint('photos', __name__)
photo_service = PhotoService()

@photos_bp.route('', methods=['GET'])
def get_photos():
    """Get photos with optional filters"""
    try:
        # Get query parameters
        user_id = request.args.get('user_id')
        review_id = request.args.get('review_id')
        limit = request.args.get('limit', 20, type=int)
        
        # Apply filters
        if user_id:
            photos = photo_service.get_photos_by_user(user_id, limit)
        elif review_id:
            photos = photo_service.get_photos_by_review(review_id, limit)
        else:
            # Get recent photos by default
            photos = photo_service.get_recent_photos(limit)
        
        return jsonify({
            'success': True,
            'photos': photos,
            'count': len(photos)
        }), 200
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@photos_bp.route('', methods=['POST'])
@jwt_required()
def create_photo():
    """Create new photo metadata"""
    try:
        user_id = get_jwt_identity()
        data = {}
        file_storage = None

        if request.content_type and 'multipart/form-data' in request.content_type.lower():
            data = request.form.to_dict()
            file_storage = (
                request.files.get('photo_file')
                or request.files.get('file')
                or (next(iter(request.files.values())) if request.files else None)
            )
        elif request.is_json:
            data = request.get_json() or {}
        else:
            data = request.get_json(silent=True) or {}

        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400

        # Add user_id from JWT token
        data['user_id'] = user_id
        
        result = photo_service.create_photo(data, file_storage=file_storage)
        return jsonify({
            'success': True,
            'data': result
        }), 201
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
                'error': 'Internal server error'
            }), 500

@photos_bp.route('/files/<path:filename>', methods=['GET'])
def serve_photo_file(filename):
    """Serve uploaded photo files."""
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    if not os.path.isabs(upload_folder):
        directory = os.path.join(current_app.root_path, upload_folder)
    else:
        directory = upload_folder
    return send_from_directory(directory, filename)

@photos_bp.route('/<photo_id>', methods=['GET'])
def get_photo(photo_id):
    """Get specific photo by ID"""
    try:
        photo = photo_service.get_photo_by_id(photo_id)
        if not photo:
            return jsonify({
                'success': False,
                'error': 'Photo not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': photo
        }), 200
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@photos_bp.route('/<photo_id>', methods=['PUT'])
@jwt_required()
def update_photo(photo_id):
    """Update photo metadata (only by owner)"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        result = photo_service.update_photo(photo_id, data, user_id)
        return jsonify({
            'success': True,
            'data': result
        }), 200
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except PermissionError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 403
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@photos_bp.route('/<photo_id>', methods=['DELETE'])
@jwt_required()
def delete_photo(photo_id):
    """Delete photo (only by owner)"""
    try:
        user_id = get_jwt_identity()
        
        success = photo_service.delete_photo(photo_id, user_id)
        if not success:
            return jsonify({
                'success': False,
                'error': 'Photo not found'
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'Photo deleted successfully'
        }), 200
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except PermissionError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 403
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@photos_bp.route('/orphaned', methods=['GET'])
@jwt_required()
def get_orphaned_photos():
    """Get photos not associated with any review (owner only)"""
    try:
        user_id = get_jwt_identity()
        photos = photo_service.get_orphaned_photos(user_id)
        
        return jsonify({
            'success': True,
            'photos': photos,
            'count': len(photos)
        }), 200
        
    except PermissionError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 403
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500
