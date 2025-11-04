#!/usr/bin/env python3
"""
ReviewComment Repository for NAYA Travel Journal
"""

from typing import List, Optional

from app import db
from app.models.review_comment import ReviewComment
from app.repositories.base_repository import SQLAlchemyRepository


class ReviewCommentRepository(SQLAlchemyRepository):
    """Repository helper for ReviewComment operations."""

    def __init__(self):
        super().__init__(ReviewComment)

    def get_by_id_for_review(self, comment_id: str, review_id: str) -> Optional[ReviewComment]:
        try:
            return ReviewComment.query.filter_by(id=comment_id, review_id=review_id).first()
        except Exception:
            return None

    def list_for_review(self, review_id: str, limit: Optional[int] = None) -> List[ReviewComment]:
        try:
            query = ReviewComment.query.filter_by(review_id=review_id).order_by(ReviewComment.created_at.asc())
            if limit:
                query = query.limit(limit)
            return query.all()
        except Exception:
            return []

    def count_for_review(self, review_id: str) -> int:
        try:
            return ReviewComment.query.filter_by(review_id=review_id).count()
        except Exception:
            return 0

    def delete_for_review(self, comment_id: str, review_id: str) -> bool:
        try:
            comment = self.get_by_id_for_review(comment_id, review_id)
            if not comment:
                return False
            db.session.delete(comment)
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            return False
