#!/usr/bin/env python3
"""
User Repository for NAYA Travel Journal
"""

from typing import Optional
from app.models.user import User
from app.repositories.base_repository import SQLAlchemyRepository

class UserRepository(SQLAlchemyRepository):
    """User repository for data access operations"""
    
    # Cible le modèle User.
    def __init__(self):
        super().__init__(User)
    
    # Récupère par email.
    def get_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email address
        Args:
            email (str): User email
        Returns:
            User or None
        """
        return self.get_by_attribute(email=email)
    
    # Récupère par pseudo.
    def get_by_username(self, username: str) -> Optional[User]:
        """
        Get user by username
        Args:
            username (str): Username
        Returns:
            User or None
        """
        return self.get_by_attribute(username=username)
    
