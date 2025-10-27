#!/usr/bin/env python3
"""
Review Repository for NAYA Travel Journal
"""

from typing import List, Optional
from app.models.review import Review
from app.repositories.base_repository import SQLAlchemyRepository

class ReviewRepository(SQLAlchemyRepository):
    """Repository for Review model operations"""
    
    def __init__(self):
        super().__init__(Review)
    
    def get_by_user(self, user_id: str, limit: Optional[int] = None) -> List[Review]:
        """
        Get reviews by user
        Args:
            user_id (str): User ID
            limit (int, optional): Limit results
        Returns:
            List of user reviews
        """
        try:
            query = Review.query.filter_by(user_id=user_id).order_by(Review.created_at.desc())
            if limit:
                query = query.limit(limit)
            return query.all()
        except Exception:
            return []
    
    def get_by_place(self, place_id: str, limit: Optional[int] = None) -> List[Review]:
        """
        Get reviews for a place
        Args:
            place_id (str): Place ID
            limit (int, optional): Limit results
        Returns:
            List of place reviews
        """
        try:
            query = Review.query.filter_by(place_id=place_id).order_by(Review.created_at.desc())
            if limit:
                query = query.limit(limit)
            return query.all()
        except Exception:
            return []
    
    def get_recent_reviews(self, limit: int = 10) -> List[Review]:
        """
        Get most recent reviews
        Args:
            limit (int): Number of reviews to return
        Returns:
            List of recent reviews
        """
        try:
            return Review.query.order_by(Review.created_at.desc()).limit(limit).all()
        except Exception:
            return []
    
    def search_reviews(self, search_term: str, limit: Optional[int] = None) -> List[Review]:
        """
        Search reviews by title or content
        Args:
            search_term (str): Search term
            limit (int, optional): Limit results
        Returns:
            List of matching reviews
        """
        try:
            search_pattern = f"%{search_term}%"
            query = Review.query.filter(
                (Review.title.ilike(search_pattern)) |
                (Review.content.ilike(search_pattern))
            ).order_by(Review.created_at.desc())
            
            if limit:
                query = query.limit(limit)
            
            return query.all()
        except Exception:
            return []
    
    def get_average_rating_for_place(self, place_id: str) -> Optional[float]:
        """
        Calculate average rating for a place
        Args:
            place_id (str): Place ID
        Returns:
            Average rating or None
        """
        try:
            from app import db
            result = db.session.query(db.func.avg(Review.rating)).filter_by(place_id=place_id).scalar()
            return float(result) if result else None
        except Exception:
            return None
    
    def get_review_count_for_place(self, place_id: str) -> int:
        """
        Get number of reviews for a place
        Args:
            place_id (str): Place ID
        Returns:
            Number of reviews
        """
        try:
            return Review.query.filter_by(place_id=place_id).count()
        except Exception:
            return 0
    
    def get_review_count_for_user(self, user_id: str) -> int:
        """
        Get number of reviews by user
        Args:
            user_id (str): User ID
        Returns:
            Number of reviews
        """
        try:
            return Review.query.filter_by(user_id=user_id).count()
        except Exception:
            return 0
    
    def user_has_reviewed_place(self, user_id: str, place_id: str) -> bool:
        """
        Check if user has already reviewed a place
        Args:
            user_id (str): User ID
            place_id (str): Place ID
        Returns:
            True if user has reviewed, False otherwise
        """
        try:
            return Review.query.filter_by(user_id=user_id, place_id=place_id).first() is not None
        except Exception:
            return False
    
    def get_rating_distribution_for_place(self, place_id: str) -> dict:
        """
        Get rating distribution for a place
        Args:
            place_id (str): Place ID
        Returns:
            Dictionary with rating counts
        """
        try:
            from app import db
            
            result = db.session.query(
                Review.rating,
                db.func.count(Review.rating)
            ).filter_by(place_id=place_id).group_by(Review.rating).all()
            
            distribution = {i: 0 for i in range(1, 6)}  # Initialize 1-5 stars
            for rating, count in result:
                distribution[rating] = count
            
            return distribution
        except Exception:
            return {i: 0 for i in range(1, 6)}
