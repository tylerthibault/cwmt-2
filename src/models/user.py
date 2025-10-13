"""
User model - THIN model following constitutional principles
Contains ONLY database schema and simple serialization
"""
from src.models import db
from src.models.base_model import BaseModel


class User(BaseModel):
    """
    User database model - THIN model pattern.
    
    Contains ONLY:
    - Database schema (columns, relationships, constraints)
    - Simple serialization methods (to_dict, from_dict)
    
    Does NOT contain:
    - Business logic (belongs in src/logic/user_logic.py)
    - Validation (belongs in logic layer)
    - Complex calculations (belongs in logic layer)
    """
    __tablename__ = 'users'
    
    # User fields
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    
    def to_dict(self, include_sensitive=False):
        """
        Serialize user to dictionary.
        Simple serialization only - NO business logic.
        
        Args:
            include_sensitive (bool): Whether to include sensitive data
            
        Returns:
            dict: User data as dictionary
        """
        data = super().to_dict()
        data.update({
            'email': self.email,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'is_active': self.is_active,
            'is_admin': self.is_admin
        })
        
        # Never include password hash unless explicitly requested (for migrations, etc.)
        if include_sensitive:
            data['password_hash'] = self.password_hash
            
        return data
    
    def __repr__(self):
        """String representation"""
        return f'<User {self.username} ({self.email})>'
