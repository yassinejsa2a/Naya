#!/usr/bin/env python3
"""
Review Service for NAYA Travel Journal
"""

from datetime import datetime, date
from typing import List, Optional, Dict, Any

from app.models.place import Place
from app.models.review import Review
from app.repositories.review_repository import ReviewRepository
from app.repositories.place_repository import PlaceRepository
from app.repositories.user_repository import UserRepository
from app.services.photo_service import PhotoService

class ReviewService:
    """Service for review business logic"""
    
    def __init__(self):
        self.review_repository = ReviewRepository()
        self.place_repository = PlaceRepository()
        self.user_repository = UserRepository()
        self.photo_service = PhotoService()
    
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
        # Extract and sanitise optional place payload
        place_payload = review_data.pop('place', {}) or {}
        place_id = (review_data.get('place_id') or place_payload.get('id') or '').strip() if review_data.get('place_id') or place_payload.get('id') else None
        place_name = review_data.pop('place_name', None) or place_payload.get('name')
        place_city = review_data.pop('place_city', None) or place_payload.get('city')
        place_country = review_data.pop('place_country', None) or place_payload.get('country')
        place_description = review_data.pop('place_description', None) or place_payload.get('description')
        place_latitude = review_data.pop('place_latitude', None) or place_payload.get('latitude')
        place_longitude = review_data.pop('place_longitude', None) or place_payload.get('longitude')

        # Remove potential trailing whitespace in strings
        if isinstance(place_name, str):
            place_name = place_name.strip()
        if isinstance(place_city, str):
            place_city = place_city.strip()
        if isinstance(place_country, str):
            place_country = place_country.strip()
        if isinstance(place_description, str):
            place_description = place_description.strip()
        if isinstance(place_latitude, str) and place_latitude:
            place_latitude = place_latitude.strip()
        if isinstance(place_longitude, str) and place_longitude:
            place_longitude = place_longitude.strip()

        # Validate required fields
        required_fields = ['title', 'content', 'rating', 'user_id']
        for field in required_fields:
            if field not in review_data or not review_data[field]:
                raise ValueError(f"Missing required field: {field}")
        
        # Resolve place identifier if not provided directly
        if not place_id:
            if not all([place_name, place_city, place_country]):
                raise ValueError("Place information is required (name, city and country)")
            place = self._get_or_create_place(
                name=place_name,
                city=place_city,
                country=place_country,
                description=place_description,
                latitude=place_latitude,
                longitude=place_longitude,
            )
            place_id = place.id
        
        # Remove unused keys so the Review model receives only valid fields
        review_payload = {
            key: value for key, value in review_data.items()
        }
        review_payload['place_id'] = place_id

        # Validate rating
        rating = review_payload['rating']
        if isinstance(rating, str) and rating.isdigit():
            rating = int(rating)
        if not isinstance(rating, int) or not (1 <= rating <= 5):
            raise ValueError("Rating must be an integer between 1 and 5")
        review_payload['rating'] = rating

        # Validate user exists
        user = self.user_repository.get(review_payload['user_id'])
        if not user:
            raise ValueError("User not found")
        
        # Validate place exists
        place = self.place_repository.get(place_id)
        if not place:
            raise ValueError("Place not found")
        
        # Check if user already reviewed this place
        if self.review_repository.user_has_reviewed_place(
            review_payload['user_id'], 
            place_id
        ):
            raise ValueError("User has already reviewed this place")
        
        # Validate content length
        review_payload['title'] = review_payload['title'].strip()
        review_payload['content'] = review_payload['content'].strip()
        if len(review_payload['title']) < 3:
            raise ValueError("Title must be at least 3 characters long")
        
        if len(review_payload['content']) < 10:
            raise ValueError("Content must be at least 10 characters long")

        visit_date_raw = review_payload.pop('visit_date', None)
        if visit_date_raw:
            review_payload['visit_date'] = self._parse_visit_date(visit_date_raw)
        
        # Create review
        review = Review(**review_payload)
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
        review_data['photos'] = self._get_photos_for_review(review.id)
        
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

        requester = self.user_repository.get(user_id)
        if not requester:
            raise ValueError("User not found")
        
        # Check ownership or admin privilege
        if review.user_id != user_id and not requester.is_admin:
            raise ValueError("You can only update your own reviews")
        
        # Remove protected fields
        protected_fields = ['id', 'created_at', 'user_id', 'place_id']
        for field in protected_fields:
            update_data.pop(field, None)
        update_data.pop('place', None)
        update_data.pop('place_name', None)
        update_data.pop('place_city', None)
        update_data.pop('place_country', None)
        update_data.pop('place_description', None)
        update_data.pop('place_latitude', None)
        update_data.pop('place_longitude', None)
        
        # Validate rating if provided
        if 'rating' in update_data:
            rating = update_data['rating']
            if isinstance(rating, str) and rating.isdigit():
                rating = int(rating)
            if not isinstance(rating, int) or not (1 <= rating <= 5):
                raise ValueError("Rating must be an integer between 1 and 5")
            update_data['rating'] = rating
        
        # Validate content lengths if provided
        if 'title' in update_data:
            update_data['title'] = update_data['title'].strip()
            if len(update_data['title']) < 3:
                raise ValueError("Title must be at least 3 characters long")
        
        if 'content' in update_data:
            update_data['content'] = update_data['content'].strip()
            if len(update_data['content']) < 10:
                raise ValueError("Content must be at least 10 characters long")

        if 'visit_date' in update_data:
            if update_data['visit_date']:
                update_data['visit_date'] = self._parse_visit_date(update_data['visit_date'])
            else:
                update_data['visit_date'] = None
        
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

        requester = self.user_repository.get(user_id)
        if not requester:
            raise ValueError("User not found")

        # Check ownership or admin privilege
        if review.user_id != user_id and not requester.is_admin:
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
            review_data['place'] = place.to_dict() if place else None
            review_data['photos'] = self._get_photos_for_review(review.id)
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
            review_data['photos'] = self._get_photos_for_review(review.id)
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
            review_data['photos'] = self._get_photos_for_review(review.id)
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
            review_data['photos'] = self._get_photos_for_review(review.id)
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
            review_data['photos'] = self._get_photos_for_review(review.id)
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
        review_data['photos'] = self._get_photos_for_review(review.id)
        
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

    def _get_photos_for_review(self, review_id: str) -> List[Dict[str, Any]]:
        """Return photos associated with a review without redundant review payload."""
        photos = self.photo_service.get_photos_by_review(review_id)
        sanitized: List[Dict[str, Any]] = []
        for photo in photos:
            if not isinstance(photo, dict):
                continue
            photo_copy = dict(photo)
            photo_copy.pop('review', None)
            sanitized.append(photo_copy)
        return sanitized

    def _get_or_create_place(
        self,
        name: str,
        city: str,
        country: str,
        description: Optional[str] = None,
        latitude: Optional[Any] = None,
        longitude: Optional[Any] = None,
    ) -> Place:
        """Fetch existing place or create a new one."""
        existing = self.place_repository.get_by_identity(name, city, country)
        if existing:
            return existing

        place_kwargs: Dict[str, Any] = {
            'name': name,
            'city': city,
            'country': country,
            'description': description or ''
        }

        if latitude not in (None, ''):
            try:
                place_kwargs['latitude'] = float(latitude)
            except (TypeError, ValueError):
                raise ValueError("Latitude must be a valid number")
        if longitude not in (None, ''):
            try:
                place_kwargs['longitude'] = float(longitude)
            except (TypeError, ValueError):
                raise ValueError("Longitude must be a valid number")

        place = Place(**place_kwargs)
        return self.place_repository.create(place)

    def _parse_visit_date(self, value: Any) -> date:
        """Parse visit date from various input formats."""
        if isinstance(value, date):
            return value
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, str):
            try:
                return datetime.strptime(value.strip(), '%Y-%m-%d').date()
            except ValueError as exc:
                raise ValueError("Visit date must follow ISO format (YYYY-MM-DD)") from exc
        raise ValueError("Invalid visit date format")
