#!/usr/bin/env python3
"""
Photo Service for NAYA Travel Journal
"""

from typing import List, Optional, Dict, Any
from app.models.photo import Photo
from app.repositories.photo_repository import PhotoRepository
from app.repositories.user_repository import UserRepository
from app.repositories.review_repository import ReviewRepository

class PhotoService:
    """Service for photo business logic"""
    
    def __init__(self):
        self.photo_repository = PhotoRepository()
        self.user_repository = UserRepository()
        self.review_repository = ReviewRepository()
    
    def create_photo(self, photo_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new photo record
        Args:
            photo_data (dict): Photo metadata
        Returns:
            dict: Created photo info
        Raises:
            ValueError: If validation fails
        """
        # Validate required fields
        required_fields = ['filename', 'user_id']
        for field in required_fields:
            if field not in photo_data or not photo_data[field]:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate user exists
        user = self.user_repository.get(photo_data['user_id'])
        if not user:
            raise ValueError("User not found")
        
        # Validate review exists if provided
        if 'review_id' in photo_data and photo_data['review_id']:
            review = self.review_repository.get(photo_data['review_id'])
            if not review:
                raise ValueError("Review not found")
        
        # Validate filename
        filename = photo_data['filename']
        if not filename or len(filename.strip()) == 0:
            raise ValueError("Invalid filename format")
        
        # Create photo
        photo = Photo(
            filename=filename,
            file_path=photo_data.get('file_path', ''),
            caption=photo_data.get('caption', ''),
            user_id=photo_data['user_id'],
            review_id=photo_data.get('review_id')
        )
        
        created_photo = self.photo_repository.create(photo)
        result = created_photo.to_dict()
        
        # Add user info
        result['user'] = user.to_public_dict()
        
        # Add review info if available
        if created_photo.review_id:
            review = self.review_repository.get(created_photo.review_id)
            result['review'] = review.to_dict() if review else None
        
        return result
    
    def get_photo_by_id(self, photo_id: str) -> Optional[Dict[str, Any]]:
        """
        Get photo by ID with user and review info
        Args:
            photo_id (str): Photo ID
        Returns:
            dict or None: Photo data with user and review info
        """
        photo = self.photo_repository.get(photo_id)
        if not photo:
            return None
        
        photo_data = photo.to_dict()
        
        # Add user info
        user = self.user_repository.get(photo.user_id)
        photo_data['user'] = user.to_public_dict() if user else None
        
        # Add review info if available
        if photo.review_id:
            review = self.review_repository.get(photo.review_id)
            photo_data['review'] = review.to_dict() if review else None
        
        return photo_data
    
    def update_photo(self, photo_id: str, photo_data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """
        Update photo metadata (only by owner)
        Args:
            photo_id (str): Photo ID
            photo_data (dict): Updated photo data
            user_id (str): User ID from JWT
        Returns:
            dict: Updated photo info
        Raises:
            ValueError: If photo not found or validation fails
            PermissionError: If user is not the owner
        """
        photo = self.photo_repository.get(photo_id)
        if not photo:
            raise ValueError("Photo not found")
        
        # Check ownership
        if photo.user_id != user_id:
            raise PermissionError("You can only update your own photos")
        
        # Validate review exists if provided
        if 'review_id' in photo_data and photo_data['review_id']:
            review = self.review_repository.get(photo_data['review_id'])
            if not review:
                raise ValueError("Review not found")
        
        # Update allowed fields
        allowed_fields = ['caption', 'review_id', 'file_path']
        update_dict = {k: v for k, v in photo_data.items() if k in allowed_fields}
        
        self.photo_repository.update(photo_id, update_dict)
        updated_photo = self.photo_repository.get(photo_id)
        
        if not updated_photo:
            raise ValueError("Failed to update photo")
            
        result = updated_photo.to_dict()
        
        # Add user info
        user = self.user_repository.get(updated_photo.user_id)
        result['user'] = user.to_public_dict() if user else None
        
        # Add review info if available
        if updated_photo.review_id:
            review = self.review_repository.get(updated_photo.review_id)
            result['review'] = review.to_dict() if review else None
        
        return result
    
    def delete_photo(self, photo_id: str, user_id: str) -> bool:
        """
        Delete photo (only by owner)
        Args:
            photo_id (str): Photo ID
            user_id (str): User ID from JWT
        Returns:
            bool: True if deleted successfully
        Raises:
            ValueError: If photo not found
            PermissionError: If user is not the owner
        """
        photo = self.photo_repository.get(photo_id)
        if not photo:
            return False
        
        # Check ownership
        if photo.user_id != user_id:
            raise PermissionError("You can only delete your own photos")
        
        return self.photo_repository.delete(photo_id)
    
    def get_photos_by_user(self, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get photos by user with user and review info
        Args:
            user_id (str): User ID
            limit (int): Maximum number of photos to return
        Returns:
            list: Photos with user and review info
        """
        # Validate user exists
        user = self.user_repository.get(user_id)
        if not user:
            raise ValueError("User not found")
        
        photos = self.photo_repository.get_by_user(user_id, limit)
        result = []
        
        for photo in photos:
            photo_data = photo.to_dict()
            photo_data['user'] = user.to_public_dict()
            
            # Add review info if available
            if photo.review_id:
                review = self.review_repository.get(photo.review_id)
                photo_data['review'] = review.to_dict() if review else None
            
            result.append(photo_data)
        
        return result
    
    def get_photos_by_review(self, review_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get photos by review with user and review info
        Args:
            review_id (str): Review ID
            limit (int): Maximum number of photos to return
        Returns:
            list: Photos with user and review info
        """
        # Validate review exists
        review = self.review_repository.get(review_id)
        if not review:
            raise ValueError("Review not found")
        
        photos = self.photo_repository.get_by_review(review_id, limit)
        result = []
        
        for photo in photos:
            photo_data = photo.to_dict()
            photo_data['review'] = review.to_dict()
            
            # Add user info
            user = self.user_repository.get(photo.user_id)
            photo_data['user'] = user.to_public_dict() if user else None
            
            result.append(photo_data)
        
        return result
    
    def get_recent_photos(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get recent photos with user and review info
        Args:
            limit (int): Maximum number of photos to return
        Returns:
            list: Recent photos with user and review info
        """
        photos = self.photo_repository.get_recent_photos(limit)
        result = []
        
        for photo in photos:
            photo_data = photo.to_dict()
            
            # Add user info
            user = self.user_repository.get(photo.user_id)
            photo_data['user'] = user.to_public_dict() if user else None
            
            # Add review info if available
            if photo.review_id:
                review = self.review_repository.get(photo.review_id)
                photo_data['review'] = review.to_dict() if review else None
            
            result.append(photo_data)
        
        return result
    
    def get_orphaned_photos(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get photos not associated with any review (owner only)
        Args:
            user_id (str): User ID from JWT
        Returns:
            list: Orphaned photos owned by user
        """
        # Get all orphaned photos and filter by user
        all_orphaned = self.photo_repository.get_orphaned_photos()
        photos = [photo for photo in all_orphaned if photo.user_id == user_id]
        result = []
        
        # Get user info once
        user = self.user_repository.get(user_id)
        user_info = user.to_public_dict() if user else None
        
        for photo in photos:
            photo_data = photo.to_dict()
            photo_data['user'] = user_info
            result.append(photo_data)
        
        return result