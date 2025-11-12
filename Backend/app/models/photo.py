#!/usr/bin/env python3
"""
Photo Model for NAYA Travel Journal
"""

# Stocke les métadonnées et liens des photos uploadées.

from app import db
from app.models.base_model import BaseModel

class Photo(BaseModel):
    """Photo model for travel journal"""
    __tablename__ = 'photos'
    
    filename = db.Column(db.String(255), nullable=False)
    original_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text)
    
    # Foreign keys
    user_id = db.Column(db.String(60), db.ForeignKey('users.id'), nullable=False)
    review_id = db.Column(db.String(60), db.ForeignKey('reviews.id'), nullable=True)
    
    def __repr__(self):
        return f'<Photo {self.filename}>'
