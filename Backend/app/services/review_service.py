#!/usr/bin/env python3
"""
Review Service for NAYA Travel Journal
"""

from datetime import datetime, date
from typing import List, Optional, Dict, Any

from app.models.user import User
from app.models.place import Place
from app.models.review import Review
from app.models.review_like import ReviewLike
from app.models.review_comment import ReviewComment
from app.repositories.review_repository import ReviewRepository
from app.repositories.place_repository import PlaceRepository
from app.repositories.user_repository import UserRepository
from app.repositories.like_repository import ReviewLikeRepository
from app.repositories.comment_repository import ReviewCommentRepository
from app.services.photo_service import PhotoService

class ReviewService:
    """Service for review business logic"""
    
    def __init__(self):
        self.review_repository = ReviewRepository()
        self.place_repository = PlaceRepository()
        self.user_repository = UserRepository()
        self.photo_service = PhotoService()
        self.like_repository = ReviewLikeRepository()
        self.comment_repository = ReviewCommentRepository()

    def _serialize_comment(self, comment: ReviewComment) -> Dict[str, Any]:
        """Serialize a review comment with author metadata."""
        user = comment.user or self.user_repository.get(comment.user_id)
        return {
            'id': comment.id,
            'content': comment.content,
            'created_at': comment.created_at.isoformat() if comment.created_at else None,
            'updated_at': comment.updated_at.isoformat() if comment.updated_at else None,
            'user': user.to_public_dict() if user else None,
        }

    def _build_like_summary(self, review_id: str, current_user_id: Optional[str] = None) -> Dict[str, Any]:
        """Return like summary payload for a review."""
        likes_count = self.like_repository.count_for_review(review_id)
        liked_by_user = False
        if current_user_id:
            liked_by_user = self.like_repository.get_by_user_and_review(current_user_id, review_id) is not None
        return {
            'review_id': review_id,
            'likes_count': likes_count,
            'liked_by_user': liked_by_user,
        }

    def _serialize_review(
        self,
        review: Review,
        current_user_id: Optional[str] = None,
        include_comments: bool = False,
        comments_limit: Optional[int] = None,
        place: Optional[Place] = None,
        user: Optional['User'] = None,
    ) -> Dict[str, Any]:
        """Serialize a review with related data and aggregates."""
        review_data = review.to_dict()

        user_obj = user or review.author or self.user_repository.get(review.user_id)
        place_obj = place or self.place_repository.get(review.place_id)

        review_data['user'] = user_obj.to_public_dict() if user_obj else None
        review_data['place'] = place_obj.to_dict() if place_obj else None
        review_data['photos'] = self._get_photos_for_review(review.id)
        review_data.update(self._build_like_summary(review.id, current_user_id))

        review_data['comments_count'] = self.comment_repository.count_for_review(review.id)

        if include_comments:
            comments = self.comment_repository.list_for_review(review.id, comments_limit)
            review_data['comments'] = [self._serialize_comment(comment) for comment in comments]

        return review_data
    
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
            'review': self._serialize_review(created_review, current_user_id=review_payload['user_id'], include_comments=True)
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
            'review': self._serialize_review(updated_review, current_user_id=user_id, include_comments=True)
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
        
        # Delete associated photos before removing the review itself
        self.photo_service.delete_photos_for_review(review_id)

        # Delete review
        success = self.review_repository.delete(review_id)
        if not success:
            raise ValueError("Failed to delete review")
        
        return {'message': 'Review deleted successfully'}

    def like_review(self, review_id: str, user_id: str) -> Dict[str, Any]:
        """Register a like from a user on a review."""
        review = self.review_repository.get(review_id)
        if not review:
            raise ValueError("Review not found")

        user = self.user_repository.get(user_id)
        if not user:
            raise ValueError("User not found")

        existing = self.like_repository.get_by_user_and_review(user_id, review_id)
        if existing:
            summary = self._build_like_summary(review_id, user_id)
            summary['message'] = 'Review already liked'
            return summary

        like = ReviewLike(user_id=user_id, review_id=review_id)
        self.like_repository.create(like)

        summary = self._build_like_summary(review_id, user_id)
        summary['message'] = 'Review liked successfully'
        return summary

    def unlike_review(self, review_id: str, user_id: str) -> Dict[str, Any]:
        """Remove a like for a review by the given user."""
        review = self.review_repository.get(review_id)
        if not review:
            raise ValueError("Review not found")

        user = self.user_repository.get(user_id)
        if not user:
            raise ValueError("User not found")

        existing = self.like_repository.get_by_user_and_review(user_id, review_id)
        if existing:
            self.like_repository.delete(existing.id)

        summary = self._build_like_summary(review_id, user_id)
        summary['message'] = 'Review unliked successfully' if existing else 'Review was not liked'
        return summary

    def get_review_likes(self, review_id: str, current_user_id: Optional[str] = None) -> Dict[str, Any]:
        """Return like summary plus a short list of recent likers."""
        review = self.review_repository.get(review_id)
        if not review:
            raise ValueError("Review not found")

        likes = self.like_repository.get_likes_for_review(review_id)
        users_preview: List[Dict[str, Any]] = []
        for like in likes[:10]:
            liker = like.user or self.user_repository.get(like.user_id)
            if liker:
                users_preview.append({
                    'id': liker.id,
                    'username': liker.username,
                    'profile_photo_url': liker.profile_photo_url,
                })

        summary = self._build_like_summary(review_id, current_user_id)
        summary['users'] = users_preview
        return summary

    def add_comment(self, review_id: str, user_id: str, content: str) -> Dict[str, Any]:
        """Add a comment to a review."""
        if not content or not content.strip():
            raise ValueError("Comment content is required")

        content = content.strip()
        if len(content) < 2:
            raise ValueError("Comment content is too short")

        review = self.review_repository.get(review_id)
        if not review:
            raise ValueError("Review not found")

        user = self.user_repository.get(user_id)
        if not user:
            raise ValueError("User not found")

        comment = ReviewComment(content=content, user_id=user_id, review_id=review_id)
        created_comment = self.comment_repository.create(comment)

        return {
            'message': 'Comment added successfully',
            'comment': self._serialize_comment(created_comment),
            'comments_count': self.comment_repository.count_for_review(review_id),
        }

    def delete_comment(self, review_id: str, comment_id: str, user_id: str) -> Dict[str, Any]:
        """Delete a comment if the requester is owner or admin."""
        review = self.review_repository.get(review_id)
        if not review:
            raise ValueError("Review not found")

        user = self.user_repository.get(user_id)
        if not user:
            raise ValueError("User not found")

        comment = self.comment_repository.get_by_id_for_review(comment_id, review_id)
        if not comment:
            raise ValueError("Comment not found")

        if comment.user_id != user_id and not user.is_admin:
            raise PermissionError("You can only delete your own comments")

        deleted = self.comment_repository.delete(comment_id)
        if not deleted:
            raise ValueError("Failed to delete comment")

        return {
            'message': 'Comment deleted successfully',
            'comments_count': self.comment_repository.count_for_review(review_id),
        }

    def list_comments(self, review_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Return comments for a given review."""
        review = self.review_repository.get(review_id)
        if not review:
            raise ValueError("Review not found")

        comments = self.comment_repository.list_for_review(review_id, limit)
        return [self._serialize_comment(comment) for comment in comments]

    def get_liked_reviews_for_user(self, user_id: str, limit: Optional[int] = None) -> Dict[str, Any]:
        """Return reviews liked by the specified user."""
        user = self.user_repository.get(user_id)
        if not user:
            raise ValueError("User not found")

        review_ids = self.like_repository.list_review_ids_for_user(user_id)
        total = len(review_ids)
        if limit:
            review_ids = review_ids[:limit]

        liked_reviews: List[Dict[str, Any]] = []
        for liked_review_id in review_ids:
            review = self.review_repository.get(liked_review_id)
            if review:
                liked_reviews.append(self._serialize_review(review, current_user_id=user_id))

        return {
            'reviews': liked_reviews,
            'total': total,
        }
    
    def get_reviews_by_place(
        self,
        place_id: str,
        limit: Optional[int] = 20,
        current_user_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get reviews for a place
        Args:
            place_id (str): Place ID
            limit (int, optional): Limit results
            current_user_id (str, optional): Current user for like context
        Returns:
            List of reviews with user data
        """
        place = self.place_repository.get(place_id)
        if not place:
            raise ValueError("Place not found")
        
        reviews = self.review_repository.get_by_place(place_id, limit)
        return [
            self._serialize_review(review, current_user_id=current_user_id, place=place)
            for review in reviews
        ]
    
    def get_reviews_by_user(
        self,
        user_id: str,
        limit: Optional[int] = 20,
        current_user_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get reviews by user
        Args:
            user_id (str): User ID
            limit (int, optional): Limit results
            current_user_id (str, optional): Current user for like context
        Returns:
            List of reviews with place data
        """
        user = self.user_repository.get(user_id)
        if not user:
            raise ValueError("User not found")
        
        reviews = self.review_repository.get_by_user(user_id, limit)
        return [
            self._serialize_review(review, current_user_id=current_user_id)
            for review in reviews
        ]
    
    def get_recent_reviews(
        self,
        limit: int = 10,
        current_user_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get recent reviews
        Args:
            limit (int): Number of reviews
            current_user_id (str, optional): Current user for like context
        Returns:
            List of recent reviews with user and place data
        """
        reviews = self.review_repository.get_recent_reviews(limit)
        return [
            self._serialize_review(review, current_user_id=current_user_id)
            for review in reviews
        ]
    
    def search_reviews(
        self,
        search_term: str,
        limit: Optional[int] = 20,
        current_user_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search reviews
        Args:
            search_term (str): Search term
            limit (int, optional): Limit results
            current_user_id (str, optional): Current user for like context
        Returns:
            List of matching reviews
        """
        if not search_term or not search_term.strip():
            return []
        
        reviews = self.review_repository.search_reviews(search_term.strip(), limit)
        return [
            self._serialize_review(review, current_user_id=current_user_id)
            for review in reviews
        ]
    
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
    
    def get_review_by_id(
        self,
        review_id: str,
        current_user_id: Optional[str] = None,
        include_comments: bool = True,
        comments_limit: Optional[int] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Get review by ID with user and place info
        Args:
            review_id (str): Review ID
            current_user_id (str, optional): Current user for like context
            include_comments (bool): Include comment list
            comments_limit (int, optional): Limit for comments
        Returns:
            dict or None: Review data with user and place info
        """
        review = self.review_repository.get(review_id)
        if not review:
            return None
        
        return self._serialize_review(
            review,
            current_user_id=current_user_id,
            include_comments=include_comments,
            comments_limit=comments_limit,
        )
    
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
