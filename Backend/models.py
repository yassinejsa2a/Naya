#!/usr/bin/env python3
"""
Database models for NAYA Travel Journal
Based on the ERD and class diagram from technical documentation
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

db = SQLAlchemy()

class User(db.Model):
    """User model for authentication and profile management"""
    __tablename__ = 'users'
    
    id = db.Column(db.String(60), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    reviews = db.relationship('Review', backref='author', lazy=True, cascade='all, delete-orphan')
    photos = db.relationship('Photo', backref='uploader', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert user to dictionary (exclude password)"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<User {self.username}>'


class Place(db.Model):
    """Place model for destinations and locations"""
    __tablename__ = 'places'
    
    id = db.Column(db.String(60), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100))
    description = db.Column(db.Text)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    google_place_id = db.Column(db.String(255))  # For Google Maps integration
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    reviews = db.relationship('Review', backref='place', lazy=True, cascade='all, delete-orphan')
    photos = db.relationship('Photo', backref='place', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert place to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'country': self.country,
            'city': self.city,
            'description': self.description,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'google_place_id': self.google_place_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Place {self.name}, {self.country}>'


class Review(db.Model):
    """Review model for user reviews of places"""
    __tablename__ = 'reviews'
    
    id = db.Column(db.String(60), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(60), db.ForeignKey('users.id'), nullable=False)
    place_id = db.Column(db.String(60), db.ForeignKey('places.id'), nullable=False)
    title = db.Column(db.String(200))
    text = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer)  # 1-5 stars
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert review to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'place_id': self.place_id,
            'title': self.title,
            'text': self.text,
            'rating': self.rating,
            'author': self.author.username if self.author else None,
            'place_name': self.place.name if self.place else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Review by {self.author.username if self.author else "Unknown"} for {self.place.name if self.place else "Unknown"}>'


class Photo(db.Model):
    """Photo model for user-uploaded photos"""
    __tablename__ = 'photos'
    
    id = db.Column(db.String(60), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(60), db.ForeignKey('users.id'), nullable=False)
    place_id = db.Column(db.String(60), db.ForeignKey('places.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    caption = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert photo to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'place_id': self.place_id,
            'filename': self.filename,
            'url': self.url,
            'caption': self.caption,
            'uploader': self.uploader.username if self.uploader else None,
            'place_name': self.place.name if self.place else None,
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Photo {self.filename} by {self.uploader.username if self.uploader else "Unknown"}>'