from datetime import datetime
from src.models.main import db, CRUDMixin


class Location(db.Model, CRUDMixin):
    """Location model for storing location information."""
    
    __tablename__ = 'locations'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Location Details
    name = db.Column(db.String(200), nullable=False, index=True)
    location = db.Column(db.String(500), nullable=False)
    additional_notes = db.Column(db.Text, nullable=True)
    
    # Tax Information
    tax_rate = db.Column(db.Numeric(5, 4), nullable=False, default=0.0000)  # e.g., 0.0895 for 8.95%
    
    # Status
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = db.Column(db.DateTime, nullable=True)  # For soft deletes
    
    def __repr__(self):
        return f'<Location {self.id}: {self.name}>'
    
    @classmethod
    def get_active_locations(cls):
        """Get all active (non-deleted) locations."""
        return cls.query.filter_by(is_active=True, deleted_at=None).order_by(cls.name).all()
    
    @classmethod
    def get_by_name(cls, name):
        """Get location by name."""
        return cls.query.filter_by(name=name, deleted_at=None).first()
    
    def soft_delete(self):
        """Soft delete the location by setting deleted_at timestamp."""
        self.deleted_at = datetime.utcnow()
        self.is_active = False
        self.save()
    
    def restore(self):
        """Restore a soft-deleted location."""
        self.deleted_at = None
        self.is_active = True
        self.save()
    
    def to_dict(self):
        """Convert location to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'location': self.location,
            'tax_rate': float(self.tax_rate) if self.tax_rate else 0.0,
            'additional_notes': self.additional_notes,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
