#!/usr/bin/env python3
"""
ReviewLike Repository for NAYA Travel Journal
"""

from typing import List, Optional

from app.models.review_like import ReviewLike
from app.repositories.base_repository import SQLAlchemyRepository


class ReviewLikeRepository(SQLAlchemyRepository):
    """Repository helper for ReviewLike operations."""

    # Cible le modèle ReviewLike.
    def __init__(self):
        super().__init__(ReviewLike)

    # Récupère un like pour user+avis.
    def get_by_user_and_review(self, user_id: str, review_id: str) -> Optional[ReviewLike]:
        try:
            return ReviewLike.query.filter_by(user_id=user_id, review_id=review_id).first()
        except Exception:
            return None

    # Liste les likes d'un avis.
    def get_likes_for_review(self, review_id: str) -> List[ReviewLike]:
        try:
            return ReviewLike.query.filter_by(review_id=review_id).order_by(ReviewLike.created_at.desc()).all()
        except Exception:
            return []

    # Compte les likes.
    def count_for_review(self, review_id: str) -> int:
        try:
            return ReviewLike.query.filter_by(review_id=review_id).count()
        except Exception:
            return 0

    # Liste les avis likés par l'utilisateur.
    def list_review_ids_for_user(self, user_id: str) -> List[str]:
        try:
            return [
                like.review_id
                for like in ReviewLike.query.filter_by(user_id=user_id).order_by(ReviewLike.created_at.desc()).all()
            ]
        except Exception:
            return []
