#!/usr/bin/env python3
"""
Photo Repository for NAYA Travel Journal
"""

from typing import List, Optional
from app.models.photo import Photo
from app.repositories.base_repository import SQLAlchemyRepository

class PhotoRepository(SQLAlchemyRepository):
    """Repository for Photo model operations"""
    
    # Cible le modèle Photo.
    def __init__(self):
        super().__init__(Photo)
    
    # Liste les photos d'un utilisateur.
    def get_by_user(self, user_id: str, limit: Optional[int] = None) -> List[Photo]:
        """
        Get photos by user
        Args:
            user_id (str): User ID
            limit (int, optional): Limit results
        Returns:
            List of user photos
        """
        try:
            query = Photo.query.filter_by(user_id=user_id).order_by(Photo.created_at.desc())
            if limit:
                query = query.limit(limit)
            return query.all()
        except Exception:
            return []
    
    # Liste les photos d'un avis.
    def get_by_review(self, review_id: str, limit: Optional[int] = None) -> List[Photo]:
        """
        Get photos for a review
        Args:
            review_id (str): Review ID
            limit (int, optional): Limit results
        Returns:
            List of review photos
        """
        try:
            query = Photo.query.filter_by(review_id=review_id).order_by(Photo.created_at.desc())
            if limit:
                query = query.limit(limit)
            return query.all()
        except Exception:
            return []
    
    # Liste les dernières photos.
    def get_recent_photos(self, limit: int = 20) -> List[Photo]:
        """
        Get most recent photos
        Args:
            limit (int): Number of photos to return
        Returns:
            List of recent photos
        """
        try:
            return Photo.query.order_by(Photo.created_at.desc()).limit(limit).all()
        except Exception:
            return []
    
    # Liste les photos orphelines.
    def get_orphaned_photos(self, limit: Optional[int] = None) -> List[Photo]:
        """
        Get photos not associated with any review
        Args:
            limit (int, optional): Limit results
        Returns:
            List of orphaned photos
        """
        try:
            query = Photo.query.filter(Photo.review_id.is_(None))
            
            if limit:
                query = query.limit(limit)
            
            return query.all()
        except Exception:
            return []
    
