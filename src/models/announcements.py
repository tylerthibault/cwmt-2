from datetime import datetime
from src.models.main import db, CRUDMixin


class Announcement(db.Model, CRUDMixin):
    """Announcement model for system-wide or course-specific announcements."""
    
    __tablename__ = 'announcements'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Announcement Content
    message = db.Column(db.Text, nullable=False)
    
    # Creator
    created_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Status
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = db.Column(db.DateTime, nullable=True)  # For soft deletes
    
    # Relationships
    created_by = db.relationship('User', backref=db.backref('announcements', lazy='dynamic'))
    
    def __repr__(self):
        return f'<Announcement {self.id}: {self.message[:50]}...>'
    
    @classmethod
    def get_active_announcements(cls):
        """Get all active (non-deleted) announcements."""
        return cls.query.filter_by(is_active=True, deleted_at=None).order_by(cls.created_at.desc()).all()
    
    @classmethod
    def get_recent_announcements(cls, limit=10):
        """Get recent active announcements with limit."""
        return cls.query.filter_by(is_active=True, deleted_at=None).order_by(cls.created_at.desc()).limit(limit).all()
    
    def soft_delete(self):
        """Soft delete the announcement by setting deleted_at timestamp."""
        self.deleted_at = datetime.utcnow()
        self.is_active = False
        self.save()
    
    def restore(self):
        """Restore a soft-deleted announcement."""
        self.deleted_at = None
        self.is_active = True
        self.save()
    
    def deactivate(self):
        """Deactivate the announcement without deleting."""
        self.is_active = False
        self.save()
    
    def activate(self):
        """Activate the announcement."""
        self.is_active = True
        self.save()
