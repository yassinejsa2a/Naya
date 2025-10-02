#!/usr/bin/env python3
"""
Places API endpoints
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.place_service import PlaceService

places_bp = Blueprint('places', __name__)
place_service = PlaceService()

@places_bp.route('', methods=['GET'])
def get_places():
    """Get places with optional filters"""
    try:
        # Get query parameters
        search = request.args.get('search')
        country = request.args.get('country')
        city = request.args.get('city')
        limit = request.args.get('limit', 20, type=int)
        
        # Apply filters
        places = place_service.search_places(search_term=search or '', city=city or '', country=country or '', limit=limit)
        
        return jsonify({
            'success': True,
            'places': places,
            'count': len(places)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@places_bp.route('', methods=['POST'])
@jwt_required()
def create_place():
    """Create new place"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Note: PlaceService doesn't use user_id currently
        result = place_service.create_place(data)
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

@places_bp.route('/<place_id>', methods=['GET'])
def get_place(place_id):
    """Get specific place"""
    try:
        place = place_service.get_place_by_id(place_id)
        return jsonify({
            'success': True,
            'place': place
        }), 200
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@places_bp.route('/<place_id>', methods=['PUT'])
@jwt_required()
def update_place(place_id):
    """Update place"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        result = place_service.update_place(place_id, data)
        return jsonify({
            'success': True,
            'data': result
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

@places_bp.route('/<place_id>', methods=['DELETE'])
@jwt_required()
def delete_place(place_id):
    """Delete place"""
    try:
        result = place_service.delete_place(place_id)
        return jsonify({
            'success': True,
            'data': result
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

@places_bp.route('/<place_id>/reviews', methods=['GET'])
def get_place_reviews(place_id):
    """Get reviews for place"""
    try:
        from app.services.review_service import ReviewService
        review_service = ReviewService()
        
        limit = request.args.get('limit', 20, type=int)
        reviews = review_service.get_reviews_by_place(place_id, limit)
        
        return jsonify({
            'success': True,
            'reviews': reviews,
            'count': len(reviews)
        }), 200
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@places_bp.route('/search', methods=['GET'])
def search_places():
    """Search places"""
    try:
        search_term = request.args.get('q', '')
        limit = request.args.get('limit', 20, type=int)
        
        if not search_term:
            return jsonify({
                'success': False,
                'error': 'Search term is required'
            }), 400
        
        places = place_service.search_places(search_term=search_term, limit=limit)
        return jsonify({
            'success': True,
            'places': places,
            'count': len(places)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@places_bp.route('/nearby', methods=['GET'])
def get_nearby_places():
    """Get nearby places"""
    try:
        lat = request.args.get('lat', type=float)
        lon = request.args.get('lon', type=float)
        radius = request.args.get('radius', 10.0, type=float)
        limit = request.args.get('limit', 10, type=int)
        
        if lat is None or lon is None:
            return jsonify({
                'success': False,
                'error': 'Latitude and longitude are required'
            }), 400
        
        places = place_service.get_nearby_places(lat, lon, radius, limit)
        return jsonify({
            'success': True,
            'places': places,
            'count': len(places)
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