"""
Base model class for database models
Provides common functionality for all models following thin model pattern
"""
from datetime import datetime
from src.models import db


class BaseModel(db.Model):
    """
    Base model with common functionality for all database models.
    
    Following constitutional principle: Models are THIN - only database schema,
    simple serialization, and basic constraints. NO business logic.
    """
    __abstract__ = True
    
    # Common fields for all models
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        """
        Simple serialization to dictionary.
        Override in child classes to customize serialization.
        
        Returns:
            dict: Model instance as dictionary
        """
        return {
            'id': self.id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def from_dict(self, data):
        """
        Update model instance from dictionary.
        Simple data assignment only - NO validation or business logic.
        
        Args:
            data (dict): Dictionary with field values
        """
        for field, value in data.items():
            if hasattr(self, field) and field not in ['id', 'created_at', 'updated_at']:
                setattr(self, field, value)
    
    def __repr__(self):
        """String representation of model instance"""
        return f'<{self.__class__.__name__} {self.id}>'
    
    @classmethod
    def get_all(cls):
        """
        Class method to get all instances of the model.
        
        Returns:
            list: List of all model instances
        """
        return cls.query.all()
    
    @classmethod
    def get_by_id(cls, record_id):
        """
        Class method to get a model instance by its ID.
        
        Args:
            record_id (int): ID of the record to retrieve
            
        Returns:
            instance or None: Model instance if found, else None
        """
        return cls.query.get(record_id)
    
    @classmethod
    def delete_by_id(cls, record_id):
        """
        Class method to delete a model instance by its ID.
        
        Args:
            record_id (int): ID of the record to delete
            
        Returns:
            bool: True if deleted, False if not found
        """
        instance = cls.get_by_id(record_id)
        if instance:
            db.session.delete(instance)
            db.session.commit()
            return True
        return False
    
