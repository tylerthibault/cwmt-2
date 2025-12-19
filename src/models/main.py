from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class CRUDMixin:
    """Mixin that adds CRUD convenience methods to database models."""
    
    @classmethod
    def create(cls, **kwargs):
        """Create a new record and save it to the database."""
        instance = cls(**kwargs)
        return instance.save()
    
    def save(self, commit=True):
        """Save the record to the database."""
        db.session.add(self)
        if commit:
            db.session.commit()
        return self
    
    def update(self, commit=True, **kwargs):
        """Update specific fields of a record."""
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        if commit:
            return self.save()
        return self
    
    def delete(self, commit=True):
        """Remove the record from the database."""
        db.session.delete(self)
        if commit:
            db.session.commit()
        return self
    
    @classmethod
    def get_by_id(cls, id):
        """Get a record by its primary key ID."""
        return cls.query.get(id)
    
    @classmethod
    def get_all(cls):
        """Get all records."""
        return cls.query.all()
    
    @classmethod
    def get_or_404(cls, id):
        """Get a record by ID or return 404."""
        return cls.query.get_or_404(id)
    
    @classmethod
    def filter_by(cls, **kwargs):
        """Filter records by given criteria."""
        return cls.query.filter_by(**kwargs)
    
    @classmethod
    def first_or_create(cls, **kwargs):
        """Get the first record matching criteria or create it."""
        instance = cls.query.filter_by(**kwargs).first()
        if instance:
            return instance
        return cls.create(**kwargs)
