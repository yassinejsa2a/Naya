#!/usr/bin/env python3
"""
Repository Pattern pour NAYA Travel Journal
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from app import db

class BaseRepository(ABC):
    """Abstract base repository for CRUD operations"""
    
    # Stocke le modèle ciblé.
    def __init__(self, model_class):
        self.model_class = model_class
    
    # Contrat abstrait de création.
    @abstractmethod
    def create(self, obj) -> Any:
        """Create a new object"""
        pass
    
    # Contrat abstrait de lecture.
    @abstractmethod
    def get(self, obj_id: str) -> Optional[Any]:
        """Get object by ID"""
        pass
    
    # Contrat abstrait de listing.
    @abstractmethod
    def get_all(self) -> List[Any]:
        """Get all objects"""
        pass
    
    # Contrat abstrait de mise à jour.
    @abstractmethod
    def update(self, obj_id: str, data: Dict[str, Any]) -> Optional[Any]:
        """Update object"""
        pass
    
    # Contrat abstrait de suppression.
    @abstractmethod
    def delete(self, obj_id: str) -> bool:
        """Delete object"""
        pass

class SQLAlchemyRepository(BaseRepository):
    """SQLAlchemy repository implementation"""
    
    # Crée via SQLAlchemy.
    def create(self, obj) -> Any:
        """Create a new object in database"""
        try:
            db.session.add(obj)
            db.session.commit()
            db.session.refresh(obj)  # Refresh pour recharger les données
            return obj
        except Exception as e:
            db.session.rollback()
            raise e
    
    # Récupère par id.
    def get(self, obj_id: str) -> Optional[Any]:
        """Get object by ID"""
        try:
            return db.session.get(self.model_class, obj_id)
        except Exception:
            return None
    
    # Liste avec pagination.
    def get_all(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[Any]:
        """Get all objects with optional pagination"""
        try:
            query = self.model_class.query
            
            if offset:
                query = query.offset(offset)
            
            if limit:
                query = query.limit(limit)
            
            return query.all()
        except Exception:
            return []
    
    # Met à jour un objet.
    def update(self, obj_id: str, data: Dict[str, Any]) -> Optional[Any]:
        """Update object with given data"""
        try:
            obj = self.get(obj_id)
            if not obj:
                return None
            
            for key, value in data.items():
                if hasattr(obj, key):
                    setattr(obj, key, value)
            
            obj.save()
            db.session.refresh(obj)  # Refresh après save
            return obj
        except Exception as e:
            db.session.rollback()
            raise e
    
    # Supprime un objet.
    def delete(self, obj_id: str) -> bool:
        """Delete object by ID"""
        try:
            obj = self.get(obj_id)
            if not obj:
                return False
            
            db.session.delete(obj)
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            return False
    
    # Cherche par attributs.
    def get_by_attribute(self, **kwargs) -> Optional[Any]:
        """Get object by attributes"""
        try:
            return self.model_class.query.filter_by(**kwargs).first()
        except Exception:
            return None
    
    # Liste par attributs.
    def get_all_by_attribute(self, **kwargs) -> List[Any]:
        """Get all objects matching attributes"""
        try:
            return self.model_class.query.filter_by(**kwargs).all()
        except Exception:
            return []
    
    # Compte les enregistrements.
    def count(self) -> int:
        """Count total objects"""
        try:
            return self.model_class.query.count()
        except Exception:
            return 0
    
    # Vérifie l'existence.
    def exists(self, obj_id: str) -> bool:
        """Check if object exists"""
        return self.get(obj_id) is not None
