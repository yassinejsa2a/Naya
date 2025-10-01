#!/usr/bin/env python3
"""
Photos API endpoints for NAYA Travel Journal
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Photo, Place, User
from config import Config
import os
import uuid
from werkzeug.utils import secure_filename

photos_bp = Blueprint('photos', __name__)

@photos_bp.route('/photos', methods=['GET'])
def get_photos():
    """
    Get photos with optional filtering
    Query parameters:
    - country: filter by country
    - user_id: filter by user
    - place_id: filter by place
    - limit: number of results (default 50)
    - offset: pagination offset (default 0)
    """
    try:
        # Get query parameters
        country = request.args.get('country')
        user_id = request.args.get('user_id')
        place_id = request.args.get('place_id')
        limit = min(int(request.args.get('limit', 50)), 100)  # Max 100 results
        offset = int(request.args.get('offset', 0))
        
        # Build query
        query = Photo.query
        
        if country:
            query = query.join(Place).filter(Place.country.ilike(f'%{country}%'))
        
        if user_id:
            query = query.filter(Photo.user_id == user_id)
        
        if place_id:
            query = query.filter(Photo.place_id == place_id)
        
        # Execute query with pagination
        photos = query.order_by(Photo.created_at.desc()).offset(offset).limit(limit).all()
        
        # Convert to JSON
        photos_data = [photo.to_dict() for photo in photos]
        
        return jsonify({
            "photos": photos_data,
            "count": len(photos_data),
            "offset": offset,
            "limit": limit
        }), 200
        
    except Exception as e:
        return jsonify({"error": "Failed to fetch photos"}), 500

@photos_bp.route('/photos', methods=['POST'])
@jwt_required()
def upload_photo():
    """
    Upload a new photo
    Expected form data:
    - file: image file
    - place_id: string
    - caption: string (optional)
    """
    try:
        current_user_id = get_jwt_identity()
        
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        place_id = request.form.get('place_id')
        caption = request.form.get('caption', '').strip()
        
        # Validate required fields
        if not place_id:
            return jsonify({"error": "Place ID is required"}), 400
        
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Check file type
        if not Config.allowed_file(file.filename):
            return jsonify({"error": "Invalid file type. Allowed: png, jpg, jpeg, gif"}), 400
        
        # Check if place exists
        place = Place.query.get(place_id)
        if not place:
            return jsonify({"error": "Place not found"}), 404
        
        # Create uploads directory if it doesn't exist
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        
        # Generate unique filename
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(Config.UPLOAD_FOLDER, unique_filename)
        
        # Save file
        file.save(file_path)
        
        # Create photo record
        photo = Photo(
            user_id=current_user_id,
            place_id=place_id,
            filename=unique_filename,
            url=f"/uploads/{unique_filename}",  # This would be updated for production
            caption=caption if caption else None
        )
        
        db.session.add(photo)
        db.session.commit()
        
        return jsonify({
            "message": "Photo uploaded successfully",
            "photo_id": photo.id,
            "photo": photo.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to upload photo"}), 500

@photos_bp.route('/photos/<photo_id>', methods=['GET'])
def get_photo(photo_id):
    """Get a specific photo by ID"""
    try:
        photo = Photo.query.get(photo_id)
        if not photo:
            return jsonify({"error": "Photo not found"}), 404
        
        return jsonify(photo.to_dict()), 200
        
    except Exception as e:
        return jsonify({"error": "Failed to fetch photo"}), 500

@photos_bp.route('/photos/<photo_id>', methods=['PUT'])
@jwt_required()
def update_photo(photo_id):
    """
    Update photo caption (only by the uploader)
    Expected JSON: {"caption": "string"}
    """
    try:
        current_user_id = get_jwt_identity()
        photo = Photo.query.get(photo_id)
        
        if not photo:
            return jsonify({"error": "Photo not found"}), 404
        
        # Check if user is the uploader
        if photo.user_id != current_user_id:
            return jsonify({"error": "You can only update your own photos"}), 403
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Update caption
        if 'caption' in data:
            caption = data['caption'].strip()
            if len(caption) > 500:
                return jsonify({"error": "Caption too long (max 500 characters)"}), 400
            photo.caption = caption if caption else None
        
        db.session.commit()
        
        return jsonify({
            "message": "Photo updated successfully",
            "photo": photo.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to update photo"}), 500

@photos_bp.route('/photos/<photo_id>', methods=['DELETE'])
@jwt_required()
def delete_photo(photo_id):
    """Delete a photo (only by the uploader)"""
    try:
        current_user_id = get_jwt_identity()
        photo = Photo.query.get(photo_id)
        
        if not photo:
            return jsonify({"error": "Photo not found"}), 404
        
        # Check if user is the uploader
        if photo.user_id != current_user_id:
            return jsonify({"error": "You can only delete your own photos"}), 403
        
        # Delete file from filesystem
        file_path = os.path.join(Config.UPLOAD_FOLDER, photo.filename)
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Delete from database
        db.session.delete(photo)
        db.session.commit()
        
        return jsonify({"message": "Photo deleted successfully"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to delete photo"}), 500