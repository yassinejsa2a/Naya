#!/usr/bin/env python3
"""
Reviews API endpoints for NAYA Travel Journal
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Review, Place, User

reviews_bp = Blueprint('reviews', __name__)

@reviews_bp.route('/reviews', methods=['GET'])
def get_reviews():
    """
    Get reviews with optional filtering
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
        query = Review.query
        
        if country:
            query = query.join(Place).filter(Place.country.ilike(f'%{country}%'))
        
        if user_id:
            query = query.filter(Review.user_id == user_id)
        
        if place_id:
            query = query.filter(Review.place_id == place_id)
        
        # Execute query with pagination
        reviews = query.order_by(Review.created_at.desc()).offset(offset).limit(limit).all()
        
        # Convert to JSON
        reviews_data = [review.to_dict() for review in reviews]
        
        return jsonify({
            "reviews": reviews_data,
            "count": len(reviews_data),
            "offset": offset,
            "limit": limit
        }), 200
        
    except Exception as e:
        return jsonify({"error": "Failed to fetch reviews"}), 500

@reviews_bp.route('/reviews', methods=['POST'])
@jwt_required()
def create_review():
    """
    Create a new review
    Expected JSON: {
        "place_id": "string",
        "title": "string" (optional),
        "text": "string",
        "rating": integer (1-5, optional)
    }
    """
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        if not data or not all(k in data for k in ('place_id', 'text')):
            return jsonify({"error": "Missing required fields: place_id, text"}), 400
        
        place_id = data['place_id']
        title = data.get('title', '').strip()
        text = data['text'].strip()
        rating = data.get('rating')
        
        # Validate input
        if not text:
            return jsonify({"error": "Review text cannot be empty"}), 400
        
        if len(text) > 2000:
            return jsonify({"error": "Review text too long (max 2000 characters)"}), 400
        
        if title and len(title) > 200:
            return jsonify({"error": "Title too long (max 200 characters)"}), 400
        
        if rating is not None:
            if not isinstance(rating, int) or rating < 1 or rating > 5:
                return jsonify({"error": "Rating must be an integer between 1 and 5"}), 400
        
        # Check if place exists
        place = Place.query.get(place_id)
        if not place:
            return jsonify({"error": "Place not found"}), 404
        
        # Check if user already reviewed this place
        existing_review = Review.query.filter_by(user_id=current_user_id, place_id=place_id).first()
        if existing_review:
            return jsonify({"error": "You have already reviewed this place"}), 409
        
        # Create review
        review = Review(
            user_id=current_user_id,
            place_id=place_id,
            title=title if title else None,
            text=text,
            rating=rating
        )
        
        db.session.add(review)
        db.session.commit()
        
        return jsonify({
            "message": "Review created successfully",
            "review_id": review.id,
            "review": review.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to create review"}), 500

@reviews_bp.route('/reviews/<review_id>', methods=['GET'])
def get_review(review_id):
    """Get a specific review by ID"""
    try:
        review = Review.query.get(review_id)
        if not review:
            return jsonify({"error": "Review not found"}), 404
        
        return jsonify(review.to_dict()), 200
        
    except Exception as e:
        return jsonify({"error": "Failed to fetch review"}), 500

@reviews_bp.route('/reviews/<review_id>', methods=['PUT'])
@jwt_required()
def update_review(review_id):
    """
    Update a review (only by the author)
    Expected JSON: {
        "title": "string" (optional),
        "text": "string" (optional),
        "rating": integer (optional)
    }
    """
    try:
        current_user_id = get_jwt_identity()
        review = Review.query.get(review_id)
        
        if not review:
            return jsonify({"error": "Review not found"}), 404
        
        # Check if user is the author
        if review.user_id != current_user_id:
            return jsonify({"error": "You can only update your own reviews"}), 403
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Update fields
        if 'title' in data:
            title = data['title'].strip()
            if len(title) > 200:
                return jsonify({"error": "Title too long (max 200 characters)"}), 400
            review.title = title if title else None
        
        if 'text' in data:
            text = data['text'].strip()
            if not text:
                return jsonify({"error": "Review text cannot be empty"}), 400
            if len(text) > 2000:
                return jsonify({"error": "Review text too long (max 2000 characters)"}), 400
            review.text = text
        
        if 'rating' in data:
            rating = data['rating']
            if rating is not None:
                if not isinstance(rating, int) or rating < 1 or rating > 5:
                    return jsonify({"error": "Rating must be an integer between 1 and 5"}), 400
            review.rating = rating
        
        db.session.commit()
        
        return jsonify({
            "message": "Review updated successfully",
            "review": review.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to update review"}), 500

@reviews_bp.route('/reviews/<review_id>', methods=['DELETE'])
@jwt_required()
def delete_review(review_id):
    """Delete a review (only by the author)"""
    try:
        current_user_id = get_jwt_identity()
        review = Review.query.get(review_id)
        
        if not review:
            return jsonify({"error": "Review not found"}), 404
        
        # Check if user is the author
        if review.user_id != current_user_id:
            return jsonify({"error": "You can only delete your own reviews"}), 403
        
        db.session.delete(review)
        db.session.commit()
        
        return jsonify({"message": "Review deleted successfully"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to delete review"}), 500