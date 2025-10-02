#!/usr/bin/env python3
"""
Photo Repository for NAYA Travel Journal
"""

from typing import List, Optional
from app.models.photo import Photo
from app.repositories.base_repository import SQLAlchemyRepository

class PhotoRepository(SQLAlchemyRepository):
    """Repository for Photo model operations"""
    
    def __init__(self):
        super().__init__(Photo)
    
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
    
    def get_by_filename(self, filename: str) -> Optional[Photo]:
        """
        Get photo by filename
        Args:
            filename (str): Photo filename
        Returns:
            Photo or None
        """
        try:
            return Photo.query.filter_by(filename=filename).first()
        except Exception:
            return None
    
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
    
    def search_photos(self, search_term: str, limit: Optional[int] = None) -> List[Photo]:
        """
        Search photos by description or original name
        Args:
            search_term (str): Search term
            limit (int, optional): Limit results
        Returns:
            List of matching photos
        """
        try:
            search_pattern = f"%{search_term}%"
            query = Photo.query.filter(
                (Photo.description.ilike(search_pattern)) |
                (Photo.original_name.ilike(search_pattern))
            ).order_by(Photo.created_at.desc())
            
            if limit:
                query = query.limit(limit)
            
            return query.all()
        except Exception:
            return []
    
    def get_photos_by_place(self, place_id: str, limit: Optional[int] = None) -> List[Photo]:
        """
        Get photos for a place (via reviews)
        Args:
            place_id (str): Place ID
            limit (int, optional): Limit results
        Returns:
            List of place photos
        """
        try:
            from app.models.review import Review
            from app import db
            
            query = db.session.query(Photo).join(Review).filter(Review.place_id == place_id).order_by(Photo.created_at.desc())
            
            if limit:
                query = query.limit(limit)
            
            return query.all()
        except Exception:
            return []
    
    def get_photo_count_for_user(self, user_id: str) -> int:
        """
        Get number of photos by user
        Args:
            user_id (str): User ID
        Returns:
            Number of photos
        """
        try:
            return Photo.query.filter_by(user_id=user_id).count()
        except Exception:
            return 0
    
    def get_photo_count_for_review(self, review_id: str) -> int:
        """
        Get number of photos for a review
        Args:
            review_id (str): Review ID
        Returns:
            Number of photos
        """
        try:
            return Photo.query.filter_by(review_id=review_id).count()
        except Exception:
            return 0
    
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
    
    def filename_exists(self, filename: str) -> bool:
        """
        Check if filename already exists
        Args:
            filename (str): Filename to check
        Returns:
            True if exists, False otherwise
        """
        try:
            return Photo.query.filter_by(filename=filename).first() is not None
        except Exception:
            return False
    
    def get_photos_without_description(self, limit: Optional[int] = None) -> List[Photo]:
        """
        Get photos without description
        Args:
            limit (int, optional): Limit results
        Returns:
            List of photos without description
        """
        try:
            query = Photo.query.filter(
                (Photo.description.is_(None)) | 
                (Photo.description == '')
            )
            
            if limit:
                query = query.limit(limit)
            
            return query.all()
        except Exception:
            return []
    
    def delete_by_filename(self, filename: str) -> bool:
        """
        Delete photo by filename
        Args:
            filename (str): Filename to delete
        Returns:
            True if deleted, False otherwise
        """
        try:
            photo = self.get_by_filename(filename)
            if photo:
                photo.delete()
                return True
            return False
        except Exception:
            return False
    
    def update_file_path(self, photo_id: str, new_path: str) -> bool:
        """
        Update photo file path
        Args:
            photo_id (str): Photo ID
            new_path (str): New file path
        Returns:
            True if updated, False otherwise
        """
        try:
            photo = self.get(photo_id)
            if photo:
                photo.file_path = new_path
                photo.save()
                return True
            return False
        except Exception:
            return False