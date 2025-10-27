#!/usr/bin/env python3
"""
Authentication Service for NAYA Travel Journal
"""

import os
import uuid
from datetime import timedelta
from typing import Optional

from flask import current_app
from flask_jwt_extended import create_access_token, create_refresh_token
from werkzeug.utils import secure_filename

from app.models.user import User
from app.repositories.user_repository import UserRepository

class AuthService:
    """Authentication service for user management"""
    
    def __init__(self):
        self.user_repository = UserRepository()
    
    def register_user(self, user_data):
        """
        Register a new user
        Args:
            user_data (dict): User registration data
        Returns:
            dict: Registration result with user info
        Raises:
            ValueError: If validation fails
        """
        # Validate required fields
        required_fields = ['username', 'email', 'password']
        for field in required_fields:
            if field not in user_data or not user_data[field]:
                raise ValueError(f"Missing required field: {field}")
        
        # Check if user already exists
        if self.user_repository.get_by_email(user_data['email']):
            raise ValueError("Email already registered")
        
        if self.user_repository.get_by_username(user_data['username']):
            raise ValueError("Username already taken")
        
        # Create user instance
        user = User(**user_data)
        
        # Validate user data
        if not user.validate_email():
            raise ValueError("Invalid email format")
        
        if not user.validate_username():
            raise ValueError("Invalid username format")
        
        # Save user
        admin_emails = current_app.config.get('ADMIN_EMAILS', [])
        if user.email and user.email.lower() in admin_emails:
            user.is_admin = True
        created_user = self.user_repository.create(user)
        
        return {
            'message': 'User registered successfully',
            'user': created_user.to_dict()
        }
    
    def authenticate_user(self, login, password):
        """
        Authenticate user with email/username and password
        Args:
            login (str): User email or username
            password (str): User password
        Returns:
            dict: Authentication result with tokens
        Raises:
            ValueError: If authentication fails
        """
        if not login or not password:
            raise ValueError("Login and password are required")
        
        # Find user by email or username
        user = self.user_repository.get_by_email(login)
        if not user:
            user = self.user_repository.get_by_username(login)
        
        if not user:
            raise ValueError("Invalid email or password")
        
        # Check password
        if not user.check_password(password):
            raise ValueError("Invalid email or password")
        
        # Check if user is active
        if not user.is_active:
            raise ValueError("Account is deactivated")
        
        # Create JWT tokens using configured expirations
        access_token = create_access_token(
            identity=user.id,
            expires_delta=self._get_expiration('JWT_ACCESS_TOKEN_EXPIRES', timedelta(hours=1))
        )
        
        refresh_token = create_refresh_token(
            identity=user.id,
            expires_delta=self._get_expiration('JWT_REFRESH_TOKEN_EXPIRES', timedelta(days=30))
        )
        
        return {
            'message': 'Login successful',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict()
        }
    
    def _get_expiration(self, config_key, fallback):
        """Return JWT expiration delta from config with a sensible fallback."""
        value = current_app.config.get(config_key)
        return value if value is not None else fallback
    
    def get_user_profile(self, user_id):
        """
        Get user profile information
        Args:
            user_id (str): User ID
        Returns:
            dict: User profile data
        Raises:
            ValueError: If user not found
        """
        user = self.user_repository.get(user_id)
        if not user:
            raise ValueError("User not found")
        
        return user.to_dict()
    
    def update_user_profile(self, user_id, update_data):
        """
        Update user profile
        Args:
            user_id (str): User ID
            update_data (dict): Data to update
        Returns:
            dict: Updated user data
        Raises:
            ValueError: If user not found or validation fails
        """
        user = self.user_repository.get(user_id)
        if not user:
            raise ValueError("User not found")
        
        # Remove sensitive fields that shouldn't be updated directly
        sensitive_fields = ['password', 'password_hash', 'id', 'created_at', 'profile_photo', 'profile_photo_url']
        for field in sensitive_fields:
            update_data.pop(field, None)
        
        # Check for username uniqueness if updating username
        if 'username' in update_data:
            existing_user = self.user_repository.get_by_username(update_data['username'])
            if existing_user and existing_user.id != user_id:
                raise ValueError("Username already taken")
        
        # Check for email uniqueness if updating email
        if 'email' in update_data:
            existing_user = self.user_repository.get_by_email(update_data['email'])
            if existing_user and existing_user.id != user_id:
                raise ValueError("Email already registered")
        
        # Update user
        updated_user = self.user_repository.update(user_id, update_data)
        if not updated_user:
            raise ValueError("Failed to update user")
        
        return {
            'message': 'Profile updated successfully',
            'user': updated_user.to_dict()
        }
    
    def change_password(self, user_id, old_password, new_password):
        """
        Change user password
        Args:
            user_id (str): User ID
            old_password (str): Current password
            new_password (str): New password
        Returns:
            dict: Success message
        Raises:
            ValueError: If validation fails
        """
        user = self.user_repository.get(user_id)
        if not user:
            raise ValueError("User not found")
        
        # Verify current password
        if not user.check_password(old_password):
            raise ValueError("Current password is incorrect")
        
        # Validate new password
        if len(new_password) < 6:
            raise ValueError("New password must be at least 6 characters long")
        
        # Update password
        user.set_password(new_password)
        user.save()
        
        return {'message': 'Password changed successfully'}

    def update_profile_photo(self, user_id, file_storage):
        """
        Upload or replace the user's profile photo.
        Args:
            user_id (str): User identifier from JWT
            file_storage (FileStorage): Uploaded avatar file
        Returns:
            dict: Message and refreshed profile data
        """
        user = self.user_repository.get(user_id)
        if not user:
            raise ValueError("User not found")

        if not file_storage or not getattr(file_storage, 'filename', None):
            raise ValueError("No file provided")

        original_name = secure_filename(file_storage.filename)
        if not original_name:
            raise ValueError("Invalid file name")

        if not self._is_allowed_avatar_file(original_name):
            allowed = ", ".join(sorted(self._allowed_avatar_extensions()))
            raise ValueError(f"Unsupported file type. Allowed types: {allowed}")

        stored_filename = self._build_avatar_filename(original_name)
        destination = self._resolve_avatar_path(stored_filename)

        os.makedirs(os.path.dirname(destination), exist_ok=True)
        file_storage.save(destination)

        self._delete_avatar_file(user.profile_photo)
        user.profile_photo = stored_filename
        user.save()

        return {
            'message': 'Profile photo updated successfully',
            'profile_photo_url': user.profile_photo_url,
            'user': user.to_dict(),
        }

    def _allowed_avatar_extensions(self):
        config_extensions = current_app.config.get('AVATAR_EXTENSIONS')
        if config_extensions:
            return {ext.lower() for ext in config_extensions}
        fallback = current_app.config.get('ALLOWED_EXTENSIONS')
        if fallback:
            return {ext.lower() for ext in fallback}
        return {'png', 'jpg', 'jpeg', 'gif', 'webp'}

    def _is_allowed_avatar_file(self, filename: str) -> bool:
        if '.' not in filename:
            return False
        extension = filename.rsplit('.', 1)[1].lower()
        return extension in self._allowed_avatar_extensions()

    def _build_avatar_filename(self, original_name: str) -> str:
        extension = ''
        if '.' in original_name:
            extension = original_name.rsplit('.', 1)[1].lower()
        unique_id = uuid.uuid4().hex
        return f"{unique_id}.{extension}" if extension else unique_id

    def _avatar_storage_root(self) -> str:
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        if os.path.isabs(upload_folder):
            base_dir = upload_folder
        else:
            base_dir = os.path.join(current_app.root_path, upload_folder)
        return os.path.join(base_dir, 'avatars')

    def _resolve_avatar_path(self, filename: str) -> str:
        return os.path.join(self._avatar_storage_root(), filename)

    def _delete_avatar_file(self, stored_filename: Optional[str]) -> None:
        if not stored_filename:
            return
        try:
            path = self._resolve_avatar_path(stored_filename)
            if os.path.exists(path):
                os.remove(path)
        except OSError:
            pass
    
    def deactivate_user(self, user_id):
        """
        Deactivate user account
        Args:
            user_id (str): User ID
        Returns:
            dict: Success message
        """
        user = self.user_repository.get(user_id)
        if not user:
            raise ValueError("User not found")
        
        user.is_active = False
        user.save()
        
        return {'message': 'Account deactivated successfully'}
    
    def get_user_stats(self, user_id):
        """
        Get user statistics (reviews, photos count, etc.)
        Args:
            user_id (str): User ID
        Returns:
            dict: User statistics
        """
        user = self.user_repository.get(user_id)
        if not user:
            raise ValueError("User not found")
        
        return {
            'user_id': user_id,
            'username': user.username,
            'reviews_count': user.reviews_count,
            'photos_count': user.photos_count,
            'member_since': user.created_at.isoformat() if user.created_at else None
        }

    def get_public_profile(self, user_id):
        """
        Return limited public profile information for a user.
        Args:
            user_id (str): User identifier
        Returns:
            dict: Public profile data
        Raises:
            ValueError: If user is not found or inactive
        """
        user = self.user_repository.get(user_id)
        if not user or not user.is_active:
            raise ValueError("User not found")

        profile = user.to_public_dict()
        profile['reviews_count'] = user.reviews_count
        profile['photos_count'] = user.photos_count
        return profile
