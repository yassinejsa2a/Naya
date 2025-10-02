#!/usr/bin/env python3
"""
Review Service for NAYA Travel Journal
"""

from typing import List, Optional, Dict, Any
from app.models.review import Review
from app.repositories.review_repository import ReviewRepository
from app.repositories.place_repository import PlaceRepository
from app.repositories.user_repository import UserRepository

class ReviewService:
    """Service for review business logic"""
    
    def __init__(self):
        self.review_repository = ReviewRepository()
        self.place_repository = PlaceRepository()
        self.user_repository = UserRepository()
    
    def create_review(self, review_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new review
        Args:
            review_data (dict): Review data
        Returns:
            dict: Created review info
        Raises:
            ValueError: If validation fails
        """
        # Validate required fields
        required_fields = ['title', 'content', 'rating', 'user_id', 'place_id']
        for field in required_fields:
            if field not in review_data or not review_data[field]:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate rating
        rating = review_data['rating']
        if not isinstance(rating, int) or not (1 <= rating <= 5):
            raise ValueError("Rating must be an integer between 1 and 5")
        
        # Validate user exists
        user = self.user_repository.get(review_data['user_id'])
        if not user:
            raise ValueError("User not found")
        
        # Validate place exists
        place = self.place_repository.get(review_data['place_id'])
        if not place:
            raise ValueError("Place not found")
        
        # Check if user already reviewed this place
        if self.review_repository.user_has_reviewed_place(
            review_data['user_id'], 
            review_data['place_id']
        ):
            raise ValueError("User has already reviewed this place")
        
        # Validate content length
        if len(review_data['title'].strip()) < 3:
            raise ValueError("Title must be at least 3 characters long")
        
        if len(review_data['content'].strip()) < 10:
            raise ValueError("Content must be at least 10 characters long")
        
        # Create review
        review = Review(**review_data)
        created_review = self.review_repository.create(review)
        
        return {
            'message': 'Review created successfully',
            'review': created_review.to_dict()
        }
    
    def get_review(self, review_id: str) -> Dict[str, Any]:
        """
        Get review by ID
        Args:
            review_id (str): Review ID
        Returns:
            dict: Review info with place and user data
        Raises:
            ValueError: If review not found
        """
        review = self.review_repository.get(review_id)
        if not review:
            raise ValueError("Review not found")
        
        # Get related data
        place = self.place_repository.get(review.place_id)
        user = self.user_repository.get(review.user_id)
        
        review_data = review.to_dict()
        review_data['place'] = place.to_dict() if place else None
        review_data['user'] = user.to_public_dict() if user else None
        
        return review_data
    
    def update_review(self, review_id: str, update_data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """
        Update review (only by author)
        Args:
            review_id (str): Review ID
            update_data (dict): Data to update
            user_id (str): User making the request
        Returns:
            dict: Updated review info
        Raises:
            ValueError: If validation fails
        """
        review = self.review_repository.get(review_id)
        if not review:
            raise ValueError("Review not found")
        
        # Check ownership
        if review.user_id != user_id:
            raise ValueError("You can only update your own reviews")
        
        # Remove protected fields
        protected_fields = ['id', 'created_at', 'user_id', 'place_id']
        for field in protected_fields:
            update_data.pop(field, None)
        
        # Validate rating if provided
        if 'rating' in update_data:
            rating = update_data['rating']
            if not isinstance(rating, int) or not (1 <= rating <= 5):
                raise ValueError("Rating must be an integer between 1 and 5")
        
        # Validate content lengths if provided
        if 'title' in update_data and len(update_data['title'].strip()) < 3:
            raise ValueError("Title must be at least 3 characters long")
        
        if 'content' in update_data and len(update_data['content'].strip()) < 10:
            raise ValueError("Content must be at least 10 characters long")
        
        # Update review
        updated_review = self.review_repository.update(review_id, update_data)
        if not updated_review:
            raise ValueError("Failed to update review")
        
        return {
            'message': 'Review updated successfully',
            'review': updated_review.to_dict()
        }
    
    def delete_review(self, review_id: str, user_id: str) -> Dict[str, Any]:
        """
        Delete a review (only by author)
        Args:
            review_id (str): Review ID
            user_id (str): User making the request
        Returns:
            dict: Success message
        Raises:
            ValueError: If review not found or unauthorized
        """
        review = self.review_repository.get(review_id)
        if not review:
            raise ValueError("Review not found")
        
        # Check ownership
        if review.user_id != user_id:
            raise ValueError("You can only delete your own reviews")
        
        # Delete review
        success = self.review_repository.delete(review_id)
        if not success:
            raise ValueError("Failed to delete review")
        
        return {'message': 'Review deleted successfully'}
    
    def get_reviews_by_place(self, place_id: str, limit: Optional[int] = 20) -> List[Dict[str, Any]]:
        """
        Get reviews for a place
        Args:
            place_id (str): Place ID
            limit (int, optional): Limit results
        Returns:
            List of reviews with user data
        """
        # Validate place exists
        place = self.place_repository.get(place_id)
        if not place:
            raise ValueError("Place not found")
        
        reviews = self.review_repository.get_by_place(place_id, limit)
        result = []
        
        for review in reviews:
            review_data = review.to_dict()
            # Add user info (public only)
            user = self.user_repository.get(review.user_id)
            review_data['user'] = user.to_public_dict() if user else None
            result.append(review_data)
        
        return result
    
    def get_reviews_by_user(self, user_id: str, limit: Optional[int] = 20) -> List[Dict[str, Any]]:
        """
        Get reviews by user
        Args:
            user_id (str): User ID
            limit (int, optional): Limit results
        Returns:
            List of reviews with place data
        """
        # Validate user exists
        user = self.user_repository.get(user_id)
        if not user:
            raise ValueError("User not found")
        
        reviews = self.review_repository.get_by_user(user_id, limit)
        result = []
        
        for review in reviews:
            review_data = review.to_dict()
            # Add place info
            place = self.place_repository.get(review.place_id)
            review_data['place'] = place.to_dict() if place else None
            result.append(review_data)
        
        return result
    
    def get_recent_reviews(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent reviews
        Args:
            limit (int): Number of reviews
        Returns:
            List of recent reviews with user and place data
        """
        reviews = self.review_repository.get_recent_reviews(limit)
        result = []
        
        for review in reviews:
            review_data = review.to_dict()
            # Add user and place info
            user = self.user_repository.get(review.user_id)
            place = self.place_repository.get(review.place_id)
            
            review_data['user'] = user.to_public_dict() if user else None
            review_data['place'] = place.to_dict() if place else None
            result.append(review_data)
        
        return result
    
    def get_top_rated_reviews(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get highest rated reviews
        Args:
            limit (int): Number of reviews
        Returns:
            List of top rated reviews
        """
        reviews = self.review_repository.get_top_rated_reviews(limit)
        result = []
        
        for review in reviews:
            review_data = review.to_dict()
            # Add user and place info
            user = self.user_repository.get(review.user_id)
            place = self.place_repository.get(review.place_id)
            
            review_data['user'] = user.to_public_dict() if user else None
            review_data['place'] = place.to_dict() if place else None
            result.append(review_data)
        
        return result
    
    def search_reviews(self, search_term: str, limit: Optional[int] = 20) -> List[Dict[str, Any]]:
        """
        Search reviews
        Args:
            search_term (str): Search term
            limit (int, optional): Limit results
        Returns:
            List of matching reviews
        """
        if not search_term or not search_term.strip():
            return []
        
        reviews = self.review_repository.search_reviews(search_term.strip(), limit)
        result = []
        
        for review in reviews:
            review_data = review.to_dict()
            # Add user and place info
            user = self.user_repository.get(review.user_id)
            place = self.place_repository.get(review.place_id)
            
            review_data['user'] = user.to_public_dict() if user else None
            review_data['place'] = place.to_dict() if place else None
            result.append(review_data)
        
        return result
    
    def get_review_statistics(self, place_id: str) -> Dict[str, Any]:
        """
        Get review statistics for a place
        Args:
            place_id (str): Place ID
        Returns:
            dict: Review statistics
        """
        # Validate place exists
        place = self.place_repository.get(place_id)
        if not place:
            raise ValueError("Place not found")
        
        stats = {
            'place_id': place_id,
            'place_name': place.name,
            'total_reviews': self.review_repository.get_review_count_for_place(place_id),
            'average_rating': self.review_repository.get_average_rating_for_place(place_id),
            'rating_distribution': self.review_repository.get_rating_distribution_for_place(place_id)
        }
        
        return stats
    
    def get_review_by_id(self, review_id: str) -> Optional[Dict[str, Any]]:
        """
        Get review by ID with user and place info
        Args:
            review_id (str): Review ID
        Returns:
            dict or None: Review data with user and place info
        """
        review = self.review_repository.get(review_id)
        if not review:
            return None
        
        review_data = review.to_dict()
        
        # Add user and place info
        user = self.user_repository.get(review.user_id)
        place = self.place_repository.get(review.place_id)
        
        review_data['user'] = user.to_public_dict() if user else None
        review_data['place'] = place.to_dict() if place else None
        
        return review_data
    
    def get_place_statistics(self, place_id: str) -> Dict[str, Any]:
        """
        Get place statistics (same as get_review_statistics for compatibility)
        Args:
            place_id (str): Place ID
        Returns:
            dict: Place review statistics
        """
        return self.get_review_statistics(place_id)