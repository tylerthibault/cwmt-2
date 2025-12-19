from datetime import datetime
import secrets
from .main import db, CRUDMixin


class Doorman(db.Model, CRUDMixin):
    """Doorman model for tracking user sessions and page navigation."""
    
    __tablename__ = 'doorman'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign Key to User
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Session Information
    session_token = db.Column(db.String(128), unique=True, nullable=False, index=True)
    
    # Sign In/Out Tracking
    sign_in_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    sign_out_time = db.Column(db.DateTime)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Additional Tracking
    ip_address = db.Column(db.String(45))  # IPv6 compatible
    user_agent = db.Column(db.String(255))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationship to User
    user = db.relationship('User', backref=db.backref('sessions', lazy='dynamic'))
    
    def __init__(self, user_id, ip_address=None, user_agent=None, **kwargs):
        """Initialize doorman session with auto-generated token."""
        super(Doorman, self).__init__(**kwargs)
        self.user_id = user_id
        self.session_token = self.generate_session_token()
        self.ip_address = ip_address
        self.user_agent = user_agent
    
    @staticmethod
    def generate_session_token():
        """Generate a unique session token."""
        return secrets.token_urlsafe(64)
    
    def sign_out(self):
        """Mark the session as signed out."""
        self.sign_out_time = datetime.utcnow()
        self.save()
    
    def update_activity(self):
        """Update last activity timestamp."""
        self.last_activity = datetime.utcnow()
        self.save()
    
    def is_session_active(self, timeout_minutes=30):
        """Check if session is still active based on last activity."""
        if self.sign_out_time:
            return False
        
        time_since_activity = datetime.utcnow() - self.last_activity
        return time_since_activity.total_seconds() < (timeout_minutes * 60)
    
    @classmethod
    def get_by_token(cls, token):
        """Get a session by its token."""
        return cls.query.filter_by(session_token=token).first()
    
    @classmethod
    def get_active_sessions(cls, user_id):
        """Get all active sessions for a user."""
        return cls.query.filter_by(user_id=user_id, sign_out_time=None).all()
    
    @classmethod
    def cleanup_inactive_sessions(cls, timeout_minutes=30):
        """Sign out sessions that have been inactive for too long."""
        cutoff_time = datetime.utcnow()
        inactive_sessions = cls.query.filter(
            cls.sign_out_time.is_(None)
        ).all()
        
        count = 0
        for session in inactive_sessions:
            time_since_activity = cutoff_time - session.last_activity
            if time_since_activity.total_seconds() >= (timeout_minutes * 60):
                session.sign_out_time = cutoff_time
                session.save(commit=False)
                count += 1
        
        if count > 0:
            db.session.commit()
        
        return count
    
    def __repr__(self):
        """String representation of the session."""
        status = 'Active' if not self.sign_out_time else 'Signed Out'
        return f'<Doorman Session {self.id} - User {self.user_id} - {status}>'
