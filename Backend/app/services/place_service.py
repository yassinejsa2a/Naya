#!/usr/bin/env python3
"""
Place Service for NAYA Travel Journal - Version simplifiée
"""

# Gère validation, recherche et stats des lieux.

from typing import List, Optional, Dict, Any
from app.models.place import Place
from app.repositories.place_repository import PlaceRepository
from app.repositories.review_repository import ReviewRepository

class PlaceService:
    """Service for place business logic"""
    
    # Initialise les dépôts.
    def __init__(self):
        self.place_repository = PlaceRepository()
        self.review_repository = ReviewRepository()
    
    # Crée un lieu.
    def create_place(self, place_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new place
        Args:
            place_data (dict): Place data
        Returns:
            dict: Created place info
        Raises:
            ValueError: If validation fails
        """
        # Validate required fields
        required_fields = ['name', 'city', 'country']
        for field in required_fields:
            if field not in place_data or not place_data[field]:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate coordinates if provided
        if 'latitude' in place_data and 'longitude' in place_data:
            lat = place_data['latitude']
            lon = place_data['longitude']
            if not self._validate_coordinates(lat, lon):
                raise ValueError("Invalid coordinates")
        
        # Check for duplicate places (same name, city, country)
        if self.place_repository.place_exists(
            place_data['name'], 
            place_data['city'], 
            place_data['country']
        ):
            raise ValueError("A place with this name already exists in this location")
        
        # Create place
        place = Place(
            name=place_data['name'],
            description=place_data.get('description', ''),
            city=place_data['city'],
            country=place_data['country'],
            latitude=place_data.get('latitude'),
            longitude=place_data.get('longitude')
        )
        
        created_place = self.place_repository.create(place)
        return created_place.to_dict()
    
    # Récupère un lieu avec stats.
    def get_place_by_id(self, place_id: str) -> Optional[Dict[str, Any]]:
        """
        Get place by ID with statistics
        Args:
            place_id (str): Place ID
        Returns:
            dict or None: Place data with stats
        """
        place = self.place_repository.get(place_id)
        if not place:
            return None
        
        place_data = place.to_dict()
        
        # Add statistics
        place_data['statistics'] = self.get_place_statistics(place_id)
        
        return place_data
    
    # Met à jour un lieu.
    def update_place(self, place_id: str, place_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update place
        Args:
            place_id (str): Place ID
            place_data (dict): Updated place data
        Returns:
            dict: Updated place info
        Raises:
            ValueError: If place not found or validation fails
        """
        place = self.place_repository.get(place_id)
        if not place:
            raise ValueError("Place not found")
        
        # Validate coordinates if provided
        if 'latitude' in place_data and 'longitude' in place_data:
            lat = place_data['latitude']
            lon = place_data['longitude']
            if not self._validate_coordinates(lat, lon):
                raise ValueError("Invalid coordinates")
        
        # Update allowed fields
        allowed_fields = ['name', 'description', 'city', 'country', 'latitude', 'longitude']
        update_dict = {k: v for k, v in place_data.items() if k in allowed_fields}
        
        self.place_repository.update(place_id, update_dict)
        updated_place = self.place_repository.get(place_id)
        
        if not updated_place:
            raise ValueError("Failed to update place")
            
        return updated_place.to_dict()
    
    # Supprime un lieu.
    def delete_place(self, place_id: str) -> bool:
        """
        Delete place
        Args:
            place_id (str): Place ID
        Returns:
            bool: True if deleted successfully
        """
        place = self.place_repository.get(place_id)
        if not place:
            return False
        
        return self.place_repository.delete(place_id)
    
    # Recherche des lieux.
    def search_places(self, search_term: str = '', city: str = '', country: str = '', limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search places with filters
        Args:
            search_term (str): Search in name and description
            city (str): Filter by city
            country (str): Filter by country
            limit (int): Maximum number of results
        Returns:
            list: Places with statistics
        """
        if city:
            places = self.place_repository.get_by_city(city, limit)
        elif country:
            places = self.place_repository.get_by_country(country, limit)
        elif search_term:
            places = self.place_repository.search_places(search_term, limit)
        else:
            # Get all places, ordered by creation date
            places = self.place_repository.get_all(limit)
        
        result = []
        for place in places:
            place_data = place.to_dict()
            
            # Add basic statistics
            place_data['review_count'] = self.review_repository.get_review_count_for_place(place.id)
            place_data['average_rating'] = self.review_repository.get_average_rating_for_place(place.id)
            
            result.append(place_data)
        
        return result
    
    # Trouve les lieux proches.
    def get_nearby_places(self, latitude: float, longitude: float, radius: float = 10.0, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get places near coordinates
        Args:
            latitude (float): Latitude
            longitude (float): Longitude
            radius (float): Search radius in km
            limit (int): Maximum number of results
        Returns:
            list: Nearby places with distance
        """
        if not self._validate_coordinates(latitude, longitude):
            raise ValueError("Invalid coordinates")
        
        places = self.place_repository.get_nearby_places(latitude, longitude, radius, limit)
        result = []
        
        for place in places:
            place_data = place.to_dict()
            
            # Add statistics
            place_data['review_count'] = self.review_repository.get_review_count_for_place(place.id)
            place_data['average_rating'] = self.review_repository.get_average_rating_for_place(place.id)
            
            # Calculate distance
            if place.latitude and place.longitude:
                distance = self._calculate_distance(latitude, longitude, place.latitude, place.longitude)
                place_data['distance_km'] = round(distance, 2)
            
            result.append(place_data)
        
        return result
    
    # Calcule les stats du lieu.
    def get_place_statistics(self, place_id: str) -> Dict[str, Any]:
        """
        Get detailed statistics for a place
        Args:
            place_id (str): Place ID
        Returns:
            dict: Place statistics
        """
        place = self.place_repository.get(place_id)
        if not place:
            raise ValueError("Place not found")
        
        stats = {
            'place_id': place_id,
            'place_name': place.name,
            'total_reviews': self.review_repository.get_review_count_for_place(place_id),
            'average_rating': self.review_repository.get_average_rating_for_place(place_id),
            'rating_distribution': self.review_repository.get_rating_distribution_for_place(place_id)
        }
        
        return stats
    
    # Valide les coordonnées.
    def _validate_coordinates(self, latitude: float, longitude: float) -> bool:
        """
        Validate geographic coordinates
        Args:
            latitude (float): Latitude
            longitude (float): Longitude
        Returns:
            bool: True if valid
        """
        try:
            lat = float(latitude)
            lon = float(longitude)
            return -90 <= lat <= 90 and -180 <= lon <= 180
        except (ValueError, TypeError):
            return False
    
    # Calcule la distance haversine.
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate distance between two points using Haversine formula
        Args:
            lat1, lon1: First point coordinates
            lat2, lon2: Second point coordinates
        Returns:
            float: Distance in kilometers
        """
        import math
        
        # Convert to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Earth's radius in kilometers
        r = 6371
        
        return r * c
