#!/usr/bin/env python3
"""
Place Model for NAYA Travel Journal
"""

# Contient les infos d'un lieu, ses coordonnées et avis.

from app import db
from app.models.base_model import BaseModel

class Place(BaseModel):
    """Place model for travel destinations"""
    __tablename__ = 'places'
    
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    city = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    
    # Relationships
    reviews = db.relationship('Review', backref='place', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Place {self.name}>'
