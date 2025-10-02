#!/usr/bin/env python3
"""
Reviews API endpoints
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.review_service import ReviewService

reviews_bp = Blueprint('reviews', __name__)
review_service = ReviewService()

@reviews_bp.route('', methods=['GET'])
def get_reviews():
    """Get reviews with optional filters"""
    try:
        # Get query parameters
        user_id = request.args.get('user_id')
        place_id = request.args.get('place_id')
        search = request.args.get('search')
        limit = request.args.get('limit', 20, type=int)
        
        # Apply filters
        if user_id:
            reviews = review_service.get_reviews_by_user(user_id, limit)
        elif place_id:
            reviews = review_service.get_reviews_by_place(place_id, limit)
        elif search:
            reviews = review_service.search_reviews(search, limit)
        else:
            # Get recent reviews by default
            reviews = review_service.get_recent_reviews(limit)
        
        return jsonify({
            'success': True,
            'reviews': reviews,
            'count': len(reviews)
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

@reviews_bp.route('', methods=['POST'])
@jwt_required()
def create_review():
    """Create new review"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Add user_id from JWT token
        data['user_id'] = user_id
        
        result = review_service.create_review(data)
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

@reviews_bp.route('/<review_id>', methods=['GET'])
def get_review(review_id):
    """Get specific review by ID"""
    try:
        review = review_service.get_review_by_id(review_id)
        if not review:
            return jsonify({
                'success': False,
                'error': 'Review not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': review
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

@reviews_bp.route('/<review_id>', methods=['PUT'])
@jwt_required()
def update_review(review_id):
    """Update review (only by owner)"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        result = review_service.update_review(review_id, data, user_id)
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

@reviews_bp.route('/<review_id>', methods=['DELETE'])
@jwt_required()
def delete_review(review_id):
    """Delete review (only by owner)"""
    try:
        user_id = get_jwt_identity()
        
        success = review_service.delete_review(review_id, user_id)
        if not success:
            return jsonify({
                'success': False,
                'error': 'Review not found'
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'Review deleted successfully'
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

@reviews_bp.route('/statistics/<place_id>', methods=['GET'])
def get_place_statistics(place_id):
    """Get rating statistics for a place"""
    try:
        stats = review_service.get_place_statistics(place_id)
        return jsonify({
            'success': True,
            'data': stats
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