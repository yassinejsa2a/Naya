#!/usr/bin/env python3
"""
Review Model for NAYA Travel Journal
"""

# Stocke les avis liés aux lieux, likes et commentaires.

from app import db
from app.models.base_model import BaseModel

class Review(BaseModel):
    """Review model for travel places"""
    __tablename__ = 'reviews'
    
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    visit_date = db.Column(db.Date, nullable=True)
    
    # Foreign keys
    user_id = db.Column(db.String(60), db.ForeignKey('users.id'), nullable=False)
    place_id = db.Column(db.String(60), db.ForeignKey('places.id'), nullable=False)

    likes = db.relationship('ReviewLike', back_populates='review', cascade='all, delete-orphan', lazy='dynamic')
    comments = db.relationship('ReviewComment', back_populates='review', cascade='all, delete-orphan', lazy=True)
    
    def __repr__(self):
        return f'<Review {self.title}>'
