#!/usr/bin/env python3
"""
Review Model for NAYA Travel Journal
"""

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
    
    def __repr__(self):
        return f'<Review {self.title}>'
