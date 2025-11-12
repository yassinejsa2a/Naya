#!/usr/bin/env python3
"""
ReviewComment Model for NAYA Travel Journal
"""

# Contient les commentaires utilisateurs reliés aux avis.

from app import db
from app.models.base_model import BaseModel


class ReviewComment(BaseModel):
    """Comment left by a user on a review."""

    __tablename__ = 'review_comments'

    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.String(60), db.ForeignKey('users.id'), nullable=False)
    review_id = db.Column(db.String(60), db.ForeignKey('reviews.id'), nullable=False)

    user = db.relationship('User', back_populates='review_comments')
    review = db.relationship('Review', back_populates='comments')

    def __repr__(self):
        return f'<ReviewComment {self.id} review={self.review_id}>'
