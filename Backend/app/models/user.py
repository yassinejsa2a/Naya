#!/usr/bin/env python3
"""
User Model for NAYA Travel Journal
"""

from werkzeug.security import generate_password_hash, check_password_hash
from app.models.base_model import BaseModel, db

class User(BaseModel):
    """User model for authentication and profiles"""
    __tablename__ = 'users'
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Profile information (Travel Journal specific)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    bio = db.Column(db.Text)
    location = db.Column(db.String(100))
    
    # Account status
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    
    # Relationships
    reviews = db.relationship('Review', backref='author', lazy=True, cascade='all, delete-orphan')
    photos = db.relationship('Photo', backref='uploader', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, *args, **kwargs):
        password = kwargs.pop('password', None)
        super().__init__(*args, **kwargs)
        
        if password:
            self.set_password(password)
    
    def set_password(self, password):
        """Hash password"""
        if not password or len(password) < 6:
            raise ValueError("Password must be at least 6 characters long")
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        if not password or not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert user to dictionary (exclude sensitive data)"""
        user_dict = super().to_dict()
        # Remove sensitive information
        user_dict.pop('password_hash', None)
        return user_dict
    
    def to_public_dict(self):
        """Public user information for display"""
        return {
            'id': self.id,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'bio': self.bio,
            'location': self.location,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @property
    def full_name(self):
        """Get user's full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    @property
    def reviews_count(self):
        """Get number of reviews by user"""
        return len(self.reviews)
    
    @property
    def photos_count(self):
        """Get number of photos by user"""
        return len(self.photos)
    
    def validate_email(self):
        """Validate email format"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, self.email) is not None
    
    def validate_username(self):
        """Validate username format"""
        if not self.username or len(self.username) < 3:
            return False
        # Check for valid characters (alphanumeric and underscore)
        import re
        return re.match(r'^[a-zA-Z0-9_]+$', self.username) is not None
    
    def __repr__(self):
        return f'<User {self.username}>'