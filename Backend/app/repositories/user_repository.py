#!/usr/bin/env python3
"""
User Repository for NAYA Travel Journal
"""

from typing import Optional, List
from app.models.user import User
from app.repositories.base_repository import SQLAlchemyRepository

class UserRepository(SQLAlchemyRepository):
    """User repository for data access operations"""
    
    def __init__(self):
        super().__init__(User)
    
    def get_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email address
        Args:
            email (str): User email
        Returns:
            User or None
        """
        return self.get_by_attribute(email=email)
    
    def get_by_username(self, username: str) -> Optional[User]:
        """
        Get user by username
        Args:
            username (str): Username
        Returns:
            User or None
        """
        return self.get_by_attribute(username=username)
    
    def get_active_users(self, limit: Optional[int] = None) -> List[User]:
        """
        Get all active users
        Args:
            limit (int, optional): Limit number of results
        Returns:
            List of active users
        """
        try:
            query = User.query.filter_by(is_active=True)
            
            if limit:
                query = query.limit(limit)
            
            return query.all()
        except Exception:
            return []
    
    def get_verified_users(self, limit: Optional[int] = None) -> List[User]:
        """
        Get all verified users
        Args:
            limit (int, optional): Limit number of results
        Returns:
            List of verified users
        """
        try:
            query = User.query.filter_by(is_verified=True, is_active=True)
            
            if limit:
                query = query.limit(limit)
            
            return query.all()
        except Exception:
            return []
    
    def search_users(self, search_term: str, limit: Optional[int] = None) -> List[User]:
        """
        Search users by username or full name
        Args:
            search_term (str): Search term
            limit (int, optional): Limit results
        Returns:
            List of matching users
        """
        try:
            search_pattern = f"%{search_term}%"
            query = User.query.filter(
                (User.username.ilike(search_pattern)) |
                (User.first_name.ilike(search_pattern)) |
                (User.last_name.ilike(search_pattern))
            ).filter_by(is_active=True)
            
            if limit:
                query = query.limit(limit)
            
            return query.all()
        except Exception:
            return []
    
    def get_users_by_location(self, location: str, limit: Optional[int] = None) -> List[User]:
        """
        Get users by location
        Args:
            location (str): Location to search
            limit (int, optional): Limit results
        Returns:
            List of users from location
        """
        try:
            query = User.query.filter(
                User.location.ilike(f"%{location}%")
            ).filter_by(is_active=True)
            
            if limit:
                query = query.limit(limit)
            
            return query.all()
        except Exception:
            return []
    
    def get_top_reviewers(self, limit: int = 10) -> List[User]:
        """
        Get users with most reviews
        Args:
            limit (int): Number of top reviewers to return
        Returns:
            List of top reviewers
        """
        try:
            # This would require a join with reviews table
            # For now, return active users (can be enhanced later)
            return self.get_active_users(limit=limit)
        except Exception:
            return []
    
    def deactivate_user(self, user_id: str) -> bool:
        """
        Deactivate user account
        Args:
            user_id (str): User ID
        Returns:
            bool: Success status
        """
        try:
            user = self.get(user_id)
            if not user:
                return False
            
            user.is_active = False
            user.save()
            return True
        except Exception:
            return False
    
    def activate_user(self, user_id: str) -> bool:
        """
        Activate user account
        Args:
            user_id (str): User ID
        Returns:
            bool: Success status
        """
        try:
            user = self.get(user_id)
            if not user:
                return False
            
            user.is_active = True
            user.save()
            return True
        except Exception:
            return False
    
    def verify_user(self, user_id: str) -> bool:
        """
        Verify user account
        Args:
            user_id (str): User ID
        Returns:
            bool: Success status
        """
        try:
            user = self.get(user_id)
            if not user:
                return False
            
            user.is_verified = True
            user.save()
            return True
        except Exception:
            return False
    
    def email_exists(self, email: str) -> bool:
        """
        Check if email is already registered
        Args:
            email (str): Email to check
        Returns:
            bool: True if email exists
        """
        return self.get_by_email(email) is not None
    
    def username_exists(self, username: str) -> bool:
        """
        Check if username is already taken
        Args:
            username (str): Username to check
        Returns:
            bool: True if username exists
        """
        return self.get_by_username(username) is not None