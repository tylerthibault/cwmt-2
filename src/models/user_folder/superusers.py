from datetime import datetime
from src.models.main import db, CRUDMixin
from src.models.user_folder import users


class Superuser(db.Model, CRUDMixin):
    """Superuser model with additional superuser-specific information."""
    
    __tablename__ = 'superusers'
    
    # Primary Key and Foreign Key to User
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    status_change_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationship to User
    user = db.relationship('User', backref=db.backref('superusers', lazy='dynamic'))
    
    def __init__(self, user_id, **kwargs):
        """Initialize superuser profile."""
        super(Superuser, self).__init__(**kwargs)
        self.user_id = user_id
    
    @property
    def full_name(self):
        """Return the superuser's full name from User."""
        return self.user.full_name if self.user else None
    
    @property
    def email(self):
        """Return the superuser's email from User."""
        return self.user.email if self.user else None
    
    def __repr__(self):
        """String representation of the superuser."""
        return f'<Superuser {self.id} - {self.full_name}>'

    def change_status(self, is_active: bool):
        """Change the active status of the superuser and update the status change date."""
        self.is_active = is_active
        self.status_change_date = datetime.utcnow()
        db.session.commit()