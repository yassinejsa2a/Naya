#!/usr/bin/env python3
"""
Authentication Service for NAYA Travel Journal
"""

from flask_jwt_extended import create_access_token, create_refresh_token
from datetime import timedelta
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
        created_user = self.user_repository.create(user)
        
        return {
            'message': 'User registered successfully',
            'user': created_user.to_dict()
        }
    
    def authenticate_user(self, email, password):
        """
        Authenticate user with email and password
        Args:
            email (str): User email
            password (str): User password
        Returns:
            dict: Authentication result with tokens
        Raises:
            ValueError: If authentication fails
        """
        if not email or not password:
            raise ValueError("Email and password are required")
        
        # Find user by email
        user = self.user_repository.get_by_email(email)
        if not user:
            raise ValueError("Invalid email or password")
        
        # Check password
        if not user.check_password(password):
            raise ValueError("Invalid email or password")
        
        # Check if user is active
        if not user.is_active:
            raise ValueError("Account is deactivated")
        
        # Create JWT tokens
        access_token = create_access_token(
            identity=user.id,
            expires_delta=timedelta(days=7)
        )
        
        refresh_token = create_refresh_token(
            identity=user.id,
            expires_delta=timedelta(days=30)
        )
        
        return {
            'message': 'Login successful',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict()
        }
    
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
        sensitive_fields = ['password', 'password_hash', 'id', 'created_at']
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