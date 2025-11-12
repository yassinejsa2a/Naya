#!/usr/bin/env python3
"""
ReviewLike Model for NAYA Travel Journal
"""

# Lie un utilisateur à un avis liké (paire unique).

from app import db
from app.models.base_model import BaseModel


class ReviewLike(BaseModel):
    """Association between a user and a liked review."""

    __tablename__ = 'review_likes'
    __table_args__ = (db.UniqueConstraint('user_id', 'review_id', name='uq_review_like_user_review'),)

    user_id = db.Column(db.String(60), db.ForeignKey('users.id'), nullable=False)
    review_id = db.Column(db.String(60), db.ForeignKey('reviews.id'), nullable=False)

    user = db.relationship('User', back_populates='review_likes')
    review = db.relationship('Review', back_populates='likes')

    def __repr__(self):
        return f'<ReviewLike user={self.user_id} review={self.review_id}>'
