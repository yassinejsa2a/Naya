#!/usr/bin/env python3
"""
Base Model for NAYA Travel Journal
"""

from datetime import datetime, date
import uuid

from app import db

class BaseModel(db.Model):
    """Base class for all models"""
    __abstract__ = True
    
    id = db.Column(db.String(60), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __init__(self, *args, **kwargs):
        if kwargs:
            for key, value in kwargs.items():
                if key == 'created_at' or key == 'updated_at':
                    if isinstance(value, str):
                        value = datetime.fromisoformat(value)
                if key != '__class__':
                    setattr(self, key, value)
        else:
            self.id = str(uuid.uuid4())
            self.created_at = datetime.utcnow()
            self.updated_at = datetime.utcnow()
    
    def save(self):
        """Save to database"""
        self.updated_at = datetime.utcnow()
        db.session.add(self)
        db.session.commit()
    
    def delete(self):
        """Delete from database"""
        db.session.delete(self)
        db.session.commit()
    
    def to_dict(self):
        """Convert instance to dictionary"""
        dict_repr = {}
        for key, value in self.__dict__.items():
            if key.startswith('_'):
                continue
            if isinstance(value, datetime):
                dict_repr[key] = value.isoformat()
            elif isinstance(value, date):
                dict_repr[key] = value.isoformat()
            else:
                dict_repr[key] = value
        return dict_repr
    
    def update(self, **kwargs):
        """Update instance attributes"""
        for key, value in kwargs.items():
            if hasattr(self, key) and key not in ['id', 'created_at']:
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def __str__(self):
        """String representation"""
        return f"[{self.__class__.__name__}] ({self.id}) {self.__dict__}"
    
    def __repr__(self):
        """String representation"""
        return self.__str__()
