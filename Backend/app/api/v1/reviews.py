#!/usr/bin/env python3
"""
Reviews API endpoints
"""

# Routes avis pour CRUD, likes et commentaires.

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from app.services.review_service import ReviewService

reviews_bp = Blueprint('reviews', __name__)
review_service = ReviewService()

@reviews_bp.route('', methods=['GET'])
# Liste les avis.
def get_reviews():
    """Get reviews with optional filters"""
    current_user_id = None
    try:
        verify_jwt_in_request(optional=True)
        current_user_id = get_jwt_identity()
    except Exception:
        if request.headers.get('Authorization'):
            return jsonify({'success': False, 'error': 'Invalid authentication token'}), 401

    try:
        # Get query parameters
        user_id = request.args.get('user_id')
        place_id = request.args.get('place_id')
        search = request.args.get('search')
        limit = request.args.get('limit', 20, type=int)
        
        # Apply filters
        if user_id:
            reviews = review_service.get_reviews_by_user(user_id, limit, current_user_id=current_user_id)
        elif place_id:
            reviews = review_service.get_reviews_by_place(place_id, limit, current_user_id=current_user_id)
        elif search:
            reviews = review_service.search_reviews(search, limit, current_user_id=current_user_id)
        else:
            # Get recent reviews by default
            reviews = review_service.get_recent_reviews(limit, current_user_id=current_user_id)
        
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
    except Exception:
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@reviews_bp.route('', methods=['POST'])
@jwt_required()
# Crée un avis.
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
# Récupère un avis.
def get_review(review_id):
    """Get specific review by ID"""
    current_user_id = None
    try:
        verify_jwt_in_request(optional=True)
        current_user_id = get_jwt_identity()
    except Exception:
        if request.headers.get('Authorization'):
            return jsonify({'success': False, 'error': 'Invalid authentication token'}), 401

    try:
        review = review_service.get_review_by_id(review_id, current_user_id=current_user_id, include_comments=True)
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
    except Exception:
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@reviews_bp.route('/<review_id>', methods=['PUT'])
@jwt_required()
# Met à jour un avis.
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
# Supprime un avis.
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

@reviews_bp.route('/<review_id>/likes', methods=['GET'])
@jwt_required(optional=True)
# Affiche les likes.
def get_review_likes(review_id):
    try:
        current_user_id = get_jwt_identity()
        data = review_service.get_review_likes(review_id, current_user_id)
        return jsonify({'success': True, 'data': data}), 200
    except ValueError as e:
        status = 404 if 'not found' in str(e).lower() else 400
        return jsonify({'success': False, 'error': str(e)}), status
    except Exception:
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

@reviews_bp.route('/<review_id>/likes', methods=['POST'])
@jwt_required()
# Ajoute un like.
def like_review_endpoint(review_id):
    try:
        user_id = get_jwt_identity()
        data = review_service.like_review(review_id, user_id)
        return jsonify({'success': True, 'data': data}), 200
    except ValueError as e:
        status = 404 if 'not found' in str(e).lower() else 400
        return jsonify({'success': False, 'error': str(e)}), status
    except Exception:
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

@reviews_bp.route('/<review_id>/likes', methods=['DELETE'])
@jwt_required()
# Retire un like.
def unlike_review_endpoint(review_id):
    try:
        user_id = get_jwt_identity()
        data = review_service.unlike_review(review_id, user_id)
        return jsonify({'success': True, 'data': data}), 200
    except ValueError as e:
        status = 404 if 'not found' in str(e).lower() else 400
        return jsonify({'success': False, 'error': str(e)}), status
    except Exception:
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

@reviews_bp.route('/<review_id>/comments', methods=['GET'])
@jwt_required(optional=True)
# Liste les commentaires.
def list_comments(review_id):
    try:
        limit = request.args.get('limit', type=int)
        comments = review_service.list_comments(review_id, limit)
        return jsonify({'success': True, 'comments': comments, 'count': len(comments)}), 200
    except ValueError as e:
        status = 404 if 'not found' in str(e).lower() else 400
        return jsonify({'success': False, 'error': str(e)}), status
    except Exception:
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

@reviews_bp.route('/<review_id>/comments', methods=['POST'])
@jwt_required()
# Ajoute un commentaire.
def add_comment(review_id):
    try:
        user_id = get_jwt_identity()
        data = request.get_json() or {}
        content = data.get('content')
        result = review_service.add_comment(review_id, user_id, content or '')
        return jsonify({'success': True, 'data': result}), 201
    except ValueError as e:
        status = 404 if 'not found' in str(e).lower() else 400
        return jsonify({'success': False, 'error': str(e)}), status
    except Exception:
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

@reviews_bp.route('/<review_id>/comments/<comment_id>', methods=['DELETE'])
@jwt_required()
# Supprime un commentaire.
def delete_comment(review_id, comment_id):
    try:
        user_id = get_jwt_identity()
        result = review_service.delete_comment(review_id, comment_id, user_id)
        return jsonify({'success': True, 'data': result}), 200
    except ValueError as e:
        status = 404 if 'not found' in str(e).lower() else 400
        return jsonify({'success': False, 'error': str(e)}), status
    except PermissionError as e:
        return jsonify({'success': False, 'error': str(e)}), 403
    except Exception:
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

@reviews_bp.route('/statistics/<place_id>', methods=['GET'])
# Donne les stats du lieu.
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
