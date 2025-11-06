"""
Password Reset Token model - THIN model following constitutional principles
Contains ONLY database schema and simple serialization
"""
from src.models import db
from src.models.base_model import BaseModel
from datetime import datetime, timedelta
import secrets


class PasswordResetToken(BaseModel):
    """
    Password Reset Token database model - THIN model pattern.
    
    Stores tokens for password reset requests with expiration tracking.
    
    Contains ONLY:
    - Database schema (columns, relationships, constraints)
    - Simple serialization methods (to_dict)
    
    Does NOT contain:
    - Business logic (belongs in src/logic/auth_logic.py)
    - Validation (belongs in logic layer)
    - Token generation logic (belongs in logic layer)
    """
    __tablename__ = 'password_reset_tokens'
    
    # Token fields
    token = db.Column(db.String(100), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_used = db.Column(db.Boolean, default=False, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    used_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    user = db.relationship('User', backref='password_reset_tokens')
    
    def to_dict(self):
        """
        Serialize password reset token to dictionary.
        Simple serialization only - NO business logic.
        
        Returns:
            dict: Token data as dictionary
        """
        return {
            'id': self.id,
            'token': self.token,
            'email': self.email,
            'user_id': self.user_id,
            'is_used': self.is_used,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'used_at': self.used_at.isoformat() if self.used_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def is_expired(self):
        """
        Simple check if token is expired.
        Simple helper method only - NO complex business logic.
        
        Returns:
            bool: True if token is expired
        """
        return datetime.utcnow() > self.expires_at
    
    def is_valid(self):
        """
        Simple check if token is valid (not used and not expired).
        Simple helper method only - NO complex business logic.
        
        Returns:
            bool: True if token is valid
        """
        return not self.is_used and not self.is_expired()
