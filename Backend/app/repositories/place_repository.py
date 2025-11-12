#!/usr/bin/env python3
"""
Place Repository for NAYA Travel Journal
"""

import math
from typing import List, Optional
from app.models.place import Place
from app.repositories.base_repository import SQLAlchemyRepository

class PlaceRepository(SQLAlchemyRepository):
    """Repository for Place model operations"""
    
    # Cible le modèle Place.
    def __init__(self):
        super().__init__(Place)
    
    # Cherche par nom.
    def get_by_name(self, name: str) -> Optional[Place]:
        """
        Get place by name
        Args:
            name (str): Place name
        Returns:
            Place or None
        """
        try:
            return Place.query.filter_by(name=name).first()
        except Exception:
            return None
    
    # Liste par ville.
    def get_by_city(self, city: str, limit: Optional[int] = None) -> List[Place]:
        """
        Get places by city
        Args:
            city (str): City name
            limit (int, optional): Limit results
        Returns:
            List of places
        """
        try:
            query = Place.query.filter_by(city=city)
            if limit:
                query = query.limit(limit)
            return query.all()
        except Exception:
            return []
    
    # Liste par pays.
    def get_by_country(self, country: str, limit: Optional[int] = None) -> List[Place]:
        """
        Get places by country
        Args:
            country (str): Country name
            limit (int, optional): Limit results
        Returns:
            List of places
        """
        try:
            query = Place.query.filter_by(country=country)
            if limit:
                query = query.limit(limit)
            return query.all()
        except Exception:
            return []
    
    # Recherche par texte.
    def search_places(self, search_term: str, limit: Optional[int] = None) -> List[Place]:
        """
        Search places by name, city, or country
        Args:
            search_term (str): Search term
            limit (int, optional): Limit results
        Returns:
            List of matching places
        """
        try:
            search_pattern = f"%{search_term}%"
            query = Place.query.filter(
                (Place.name.ilike(search_pattern)) |
                (Place.city.ilike(search_pattern)) |
                (Place.country.ilike(search_pattern)) |
                (Place.description.ilike(search_pattern))
            )
            
            if limit:
                query = query.limit(limit)
            
            return query.all()
        except Exception:
            return []
    
    # Trouve les lieux proches.
    def get_nearby_places(self, latitude: float, longitude: float, 
                         radius_km: float = 10.0, limit: Optional[int] = None) -> List[Place]:
        """
        Get places within radius (simple implementation)
        Args:
            latitude (float): Center latitude
            longitude (float): Center longitude
            radius_km (float): Radius in kilometers
            limit (int, optional): Limit results
        Returns:
            List of nearby places
        """
        try:
            # Simple radius calculation (not precise for large distances)
            lat_range = radius_km / 111.0  # Rough km to degree conversion
            cos_lat = math.cos(math.radians(latitude))
            lon_divisor = 111.0 * max(abs(cos_lat), 0.01)  # Avoid division by zero near poles
            lon_range = radius_km / lon_divisor
            
            query = Place.query.filter(
                Place.latitude.between(latitude - lat_range, latitude + lat_range),
                Place.longitude.between(longitude - lon_range, longitude + lon_range)
            )
            
            if limit:
                query = query.limit(limit)
            
            return query.all()
        except Exception:
            return []
    
    # Vérifie les doublons.
    def place_exists(self, name: str, city: str, country: str) -> bool:
        """
        Check if place already exists
        Args:
            name (str): Place name
            city (str): City name
            country (str): Country name
        Returns:
            True if exists, False otherwise
        """
        return Place.query.filter_by(name=name, city=city, country=country).first() is not None

    # Récupère par nom/ville/pays.
    def get_by_identity(self, name: str, city: str, country: str) -> Optional[Place]:
        """
        Get a place matching the exact name/city/country combination.
        """
        try:
            return Place.query.filter_by(name=name, city=city, country=country).first()
        except Exception:
            return None
