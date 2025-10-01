#!/usr/bin/env python3
"""
Places API endpoints for NAYA Travel Journal
Integrates with Google Maps API for place discovery
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Place
import requests
from config import Config

places_bp = Blueprint('places', __name__)

def search_google_places(query, location=None, radius=50000):
    """
    Search places using Google Maps Places API
    
    Args:
        query: Search query (e.g., "restaurants in Paris")
        location: lat,lng coordinates (optional)
        radius: Search radius in meters (default 50km)
    
    Returns:
        List of places from Google Maps API
    """
    if not Config.GOOGLE_MAPS_API_KEY:
        return []
    
    base_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    
    params = {
        'query': query,
        'key': Config.GOOGLE_MAPS_API_KEY
    }
    
    if location:
        params['location'] = location
        params['radius'] = radius
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        
        data = response.json()
        places = []
        
        for place in data.get('results', []):
            places.append({
                'name': place.get('name'),
                'address': place.get('formatted_address'),
                'rating': place.get('rating'),
                'price_level': place.get('price_level'),
                'types': place.get('types', []),
                'location': {
                    'lat': place['geometry']['location']['lat'],
                    'lng': place['geometry']['location']['lng']
                },
                'google_place_id': place.get('place_id'),
                'photos': [photo.get('photo_reference') for photo in place.get('photos', [])[:3]]
            })
        
        return places
        
    except Exception as e:
        print(f"Google Places API error: {e}")
        return []

@places_bp.route('/places', methods=['GET'])
def get_places():
    """
    Get places from database with optional filtering
    Query parameters:
    - country: filter by country
    - city: filter by city
    - limit: number of results (default 50)
    - offset: pagination offset (default 0)
    """
    try:
        # Get query parameters
        country = request.args.get('country')
        city = request.args.get('city')
        limit = min(int(request.args.get('limit', 50)), 100)  # Max 100 results
        offset = int(request.args.get('offset', 0))
        
        # Build query
        query = Place.query
        
        if country:
            query = query.filter(Place.country.ilike(f'%{country}%'))
        
        if city:
            query = query.filter(Place.city.ilike(f'%{city}%'))
        
        # Execute query with pagination
        places = query.order_by(Place.created_at.desc()).offset(offset).limit(limit).all()
        
        # Convert to JSON
        places_data = [place.to_dict() for place in places]
        
        return jsonify({
            "places": places_data,
            "count": len(places_data),
            "offset": offset,
            "limit": limit
        }), 200
        
    except Exception as e:
        return jsonify({"error": "Failed to fetch places"}), 500

@places_bp.route('/places/search', methods=['GET'])
def search_places():
    """
    Search places using Google Maps API
    Query parameters:
    - q: search query (required)
    - location: lat,lng coordinates (optional)
    - radius: search radius in meters (optional, default 50000)
    """
    try:
        query = request.args.get('q')
        location = request.args.get('location')
        radius = int(request.args.get('radius', 50000))
        
        if not query:
            return jsonify({"error": "Search query 'q' is required"}), 400
        
        # Search using Google Places API
        places = search_google_places(query, location, radius)
        
        return jsonify({
            "places": places,
            "count": len(places),
            "query": query
        }), 200
        
    except Exception as e:
        return jsonify({"error": "Failed to search places"}), 500

@places_bp.route('/places', methods=['POST'])
@jwt_required()
def create_place():
    """
    Create a new place in the database
    Expected JSON: {
        "name": "string",
        "country": "string",
        "city": "string" (optional),
        "description": "string" (optional),
        "latitude": float (optional),
        "longitude": float (optional),
        "google_place_id": "string" (optional)
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or not all(k in data for k in ('name', 'country')):
            return jsonify({"error": "Missing required fields: name, country"}), 400
        
        name = data['name'].strip()
        country = data['country'].strip()
        city = data.get('city', '').strip()
        description = data.get('description', '').strip()
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        google_place_id = data.get('google_place_id', '').strip()
        
        # Validate input
        if not name or len(name) < 2:
            return jsonify({"error": "Place name must be at least 2 characters long"}), 400
        
        if not country or len(country) < 2:
            return jsonify({"error": "Country must be at least 2 characters long"}), 400
        
        if description and len(description) > 1000:
            return jsonify({"error": "Description too long (max 1000 characters)"}), 400
        
        # Validate coordinates
        if latitude is not None and longitude is not None:
            try:
                latitude = float(latitude)
                longitude = float(longitude)
                if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
                    return jsonify({"error": "Invalid coordinates"}), 400
            except ValueError:
                return jsonify({"error": "Coordinates must be numbers"}), 400
        
        # Check if place with same name and country already exists
        existing_place = Place.query.filter_by(name=name, country=country).first()
        if existing_place:
            return jsonify({"error": "Place already exists in this country"}), 409
        
        # Create place
        place = Place(
            name=name,
            country=country,
            city=city if city else None,
            description=description if description else None,
            latitude=latitude,
            longitude=longitude,
            google_place_id=google_place_id if google_place_id else None
        )
        
        db.session.add(place)
        db.session.commit()
        
        return jsonify({
            "message": "Place created successfully",
            "place_id": place.id,
            "place": place.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to create place"}), 500

@places_bp.route('/places/<place_id>', methods=['GET'])
def get_place(place_id):
    """Get a specific place by ID"""
    try:
        place = Place.query.get(place_id)
        if not place:
            return jsonify({"error": "Place not found"}), 404
        
        # Include reviews and photos count
        place_data = place.to_dict()
        place_data['reviews_count'] = len(place.reviews)
        place_data['photos_count'] = len(place.photos)
        
        return jsonify(place_data), 200
        
    except Exception as e:
        return jsonify({"error": "Failed to fetch place"}), 500

@places_bp.route('/places/<place_id>', methods=['PUT'])
@jwt_required()
def update_place(place_id):
    """
    Update a place (for now, any authenticated user can update)
    Expected JSON: {
        "name": "string" (optional),
        "description": "string" (optional),
        "city": "string" (optional)
    }
    """
    try:
        place = Place.query.get(place_id)
        
        if not place:
            return jsonify({"error": "Place not found"}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Update fields
        if 'name' in data:
            name = data['name'].strip()
            if not name or len(name) < 2:
                return jsonify({"error": "Place name must be at least 2 characters long"}), 400
            place.name = name
        
        if 'description' in data:
            description = data['description'].strip()
            if len(description) > 1000:
                return jsonify({"error": "Description too long (max 1000 characters)"}), 400
            place.description = description if description else None
        
        if 'city' in data:
            city = data['city'].strip()
            place.city = city if city else None
        
        db.session.commit()
        
        return jsonify({
            "message": "Place updated successfully",
            "place": place.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to update place"}), 500