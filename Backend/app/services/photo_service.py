#!/usr/bin/env python3
"""
Photo Service for NAYA Travel Journal
"""

import os
import uuid
from typing import List, Optional, Dict, Any

from flask import current_app, url_for
from werkzeug.routing import BuildError
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

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
    
    def create_photo(self, photo_data: Dict[str, Any], file_storage: Optional[FileStorage] = None) -> Dict[str, Any]:
        """
        Create a new photo record
        Args:
            photo_data (dict): Photo metadata
            file_storage (FileStorage, optional): Uploaded photo file
        Returns:
            dict: Created photo info
        Raises:
            ValueError: If validation fails
        """
        # Validate required fields
        user_id = photo_data.get('user_id')
        if not user_id:
            raise ValueError("Missing required field: user_id")
        
        # Normalise review identifier
        review_id = photo_data.get('review_id')
        if isinstance(review_id, str):
            review_id = review_id.strip() or None
        if not review_id:
            review_id = None
        
        file_storage = file_storage if file_storage and getattr(file_storage, 'filename', None) else None

        if file_storage:
            original_name = secure_filename(file_storage.filename)
            if not original_name:
                raise ValueError("Invalid file name")
            
            if not self._allowed_file(original_name):
                allowed = ", ".join(sorted(self._allowed_extensions()))
                raise ValueError(f"Unsupported file type. Allowed types: {allowed}")
            
            stored_filename = self._build_unique_filename(original_name)
            storage_path, relative_path = self._resolve_storage_paths(stored_filename)
            self._save_file(file_storage, storage_path)
        else:
            raise ValueError("A photo file must be provided")
        
        description = (
            photo_data.get('description') or
            photo_data.get('caption') or
            ''
        )
        
        # Validate user exists
        user = self.user_repository.get(user_id)
        if not user:
            raise ValueError("User not found")
        
        review_obj = None
        # Validate review exists if provided
        if review_id:
            review_obj = self.review_repository.get(review_id)
            if not review_obj:
                raise ValueError("Review not found")
            if review_obj.user_id != user_id and not user.is_admin:
                raise PermissionError("You can only add photos to your own reviews")
        
        # Create photo
        photo = Photo(
            filename=stored_filename,
            original_name=original_name,
            file_path=relative_path,
            description=description,
            user_id=user_id,
            review_id=review_id
        )
        
        created_photo = self.photo_repository.create(photo)
        return self._build_photo_response(created_photo, user=user, review=review_obj)
    
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
        
        return self._build_photo_response(photo)
    
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

        requester = self.user_repository.get(user_id)
        if not requester:
            raise ValueError("User not found")
        
        # Check ownership
        if photo.user_id != user_id and not requester.is_admin:
            raise PermissionError("You can only update your own photos")
        
        # Validate review exists if provided
        if 'review_id' in photo_data and photo_data['review_id']:
            review = self.review_repository.get(photo_data['review_id'])
            if not review:
                raise ValueError("Review not found")
            if review.user_id != user_id and not requester.is_admin:
                raise PermissionError("You can only link photos to your own reviews")
        # Normalise keys
        if 'caption' in photo_data and 'description' not in photo_data:
            photo_data['description'] = photo_data['caption']
        
        # Update allowed fields
        allowed_fields = ['description', 'review_id']
        update_dict = {k: v for k, v in photo_data.items() if k in allowed_fields}
        
        self.photo_repository.update(photo_id, update_dict)
        updated_photo = self.photo_repository.get(photo_id)
        
        if not updated_photo:
            raise ValueError("Failed to update photo")
            
        return self._build_photo_response(updated_photo)

    def delete_photos_for_review(self, review_id: str) -> int:
        """Force delete every photo associated with a review."""
        photos = self.photo_repository.get_by_review(review_id)
        removed = 0
        for photo in photos:
            file_path = photo.file_path
            if not self.photo_repository.delete(photo.id):
                raise ValueError("Failed to delete associated photo")
            self._delete_file(file_path)
            removed += 1
        return removed
    
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

        requester = self.user_repository.get(user_id)
        if not requester:
            raise ValueError("User not found")
        
        # Check ownership
        if photo.user_id != user_id and not requester.is_admin:
            raise PermissionError("You can only delete your own photos")
        
        removed = self.photo_repository.delete(photo_id)
        if removed:
            self._delete_file(photo.file_path)
        return removed
    
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
            result.append(self._build_photo_response(photo, user=user))
        
        return result

    def _build_unique_filename(self, original_name: str) -> str:
        """Build a unique filename preserving the extension."""
        extension = ''
        if '.' in original_name:
            extension = original_name.rsplit('.', 1)[1].lower()
        unique_id = uuid.uuid4().hex
        return f"{unique_id}.{extension}" if extension else unique_id

    def _allowed_extensions(self):
        config_extensions = current_app.config.get('ALLOWED_EXTENSIONS')
        if config_extensions:
            return {ext.lower() for ext in config_extensions}
        return {'png', 'jpg', 'jpeg', 'gif', 'webp'}

    def _allowed_file(self, filename: str) -> bool:
        """Check if the file extension is allowed."""
        if '.' not in filename:
            return False
        extension = filename.rsplit('.', 1)[1].lower()
        return extension in self._allowed_extensions()

    def _resolve_storage_paths(self, filename: str):
        """Compute absolute storage path and relative DB path."""
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        if os.path.isabs(upload_folder):
            storage_dir = upload_folder
            relative_path = os.path.join(upload_folder, filename)
        else:
            storage_dir = os.path.join(current_app.root_path, upload_folder)
            relative_path = os.path.join(upload_folder, filename)
        os.makedirs(storage_dir, exist_ok=True)
        absolute_path = os.path.join(storage_dir, filename)
        return absolute_path, relative_path

    def _save_file(self, file_storage: FileStorage, destination: str) -> None:
        """Persist the uploaded file on disk."""
        file_storage.save(destination)

    def _delete_file(self, file_path: Optional[str]) -> None:
        """Remove a file from disk if it exists."""
        if not file_path:
            return
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        if os.path.isabs(file_path):
            absolute_path = file_path
        else:
            if os.path.isabs(upload_folder):
                absolute_path = os.path.join(upload_folder, os.path.basename(file_path))
            else:
                absolute_path = os.path.join(current_app.root_path, file_path)
        if os.path.exists(absolute_path):
            try:
                os.remove(absolute_path)
            except OSError:
                pass

    def _build_photo_response(self, photo: Photo, user=None, review=None) -> Dict[str, Any]:
        """Build a serialisable representation for a photo instance."""
        data = photo.to_dict()

        if user is None:
            user = self.user_repository.get(photo.user_id)
        data['user'] = user.to_public_dict() if user else None

        if photo.review_id:
            if review is None:
                review = self.review_repository.get(photo.review_id)
            data['review'] = review.to_dict() if review else None
        else:
            data['review'] = None

        try:
            data['file_url'] = url_for('v1.photos.serve_photo_file', filename=photo.filename, _external=True)
        except BuildError:
            try:
                data['file_url'] = url_for('photos.serve_photo_file', filename=photo.filename, _external=True)
            except RuntimeError:
                data['file_url'] = None
            except BuildError:
                data['file_url'] = None
        except RuntimeError:
            data['file_url'] = None
        data['caption'] = data.get('description')
        return data
    
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
        return [self._build_photo_response(photo, review=review) for photo in photos]
    
    def get_recent_photos(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get recent photos with user and review info
        Args:
            limit (int): Maximum number of photos to return
        Returns:
            list: Recent photos with user and review info
        """
        photos = self.photo_repository.get_recent_photos(limit)
        return [self._build_photo_response(photo) for photo in photos]
    
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
        user = self.user_repository.get(user_id)
        return [self._build_photo_response(photo, user=user) for photo in photos]
