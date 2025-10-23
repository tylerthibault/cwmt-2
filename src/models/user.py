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
    email_confirmed = db.Column(db.Boolean, default=False, nullable=False)
    email_confirmed_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    roles = db.relationship('UserHasRoles', back_populates='user', cascade='all, delete-orphan', overlaps="role_list,users_list")
    role_list = db.relationship('Role', secondary='user_has_roles', backref='users_list', overlaps="roles")
    logbooks = db.relationship('Logbook', back_populates='user', cascade='all, delete-orphan')
    # student_profile relationship is defined in StudentProfile model as backref
    
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
            'is_admin': self.is_admin,
            'email_confirmed': self.email_confirmed,
            'email_confirmed_at': self.email_confirmed_at
        })
        
        # Never include password hash unless explicitly requested (for migrations, etc.)
        if include_sensitive:
            data['password_hash'] = self.password_hash
            
        return data
    
    def __repr__(self):
        """String representation"""
        return f'<User {self.username} ({self.email})>'
    

    @classmethod
    def create(cls, **kwargs):
        """
        Create and save a new user.
        
        Args:
            kwargs: User fields

        Returns:
            User: The created user instance
        """
        user = cls(**kwargs)
        db.session.add(user)
        db.session.commit()
        return user
    
    @classmethod
    def get_by_id(cls, user_id):
        """
        Get user by ID.
        
        Args:
            user_id (int): ID of the user
            
        Returns:
            User: The user instance or None if not found
        """
        return cls.query.get(user_id)
    
    @classmethod
    def get_by_email(cls, email):
        """
        Get user by email.
        
        Args:
            email (str): Email of the user
            
        Returns:
            User: The user instance or None if not found
        """
        return cls.query.filter_by(email=email).first()
    
    @classmethod
    def get_all(cls):
        """
        Get all users.
        
        Returns:
            list: List of all user instances
        """
        return cls.query.all()
    
    @classmethod
    def update(cls, user_id, **kwargs):
        """
        Update user fields.
        
        Args:
            user_id (int): ID of the user to update
            kwargs: Fields to update
            
        Returns:
            User: The updated user instance or None if not found
        """
        user = cls.query.get(user_id)
        if user:
            for key, value in kwargs.items():
                setattr(user, key, value)
            db.session.commit()
            return user
        return None
    
    @classmethod
    def deactivate(cls, user_id):
        """
        Deactivate a user by setting is_active to False.
        
        Args:
            user_id (int): ID of the user to deactivate
            
        Returns:
            bool: True if deactivated, False if user not found
        """
        user = cls.query.get(user_id)
        if user:
            user.is_active = False
            db.session.commit()
            return True
        return False
    

    @classmethod
    def activate(cls, user_id):
        """
        Activate a user by setting is_active to True.
        
        Args:
            user_id (int): ID of the user to activate
            
        Returns:
            bool: True if activated, False if user not found
        """
        user = cls.query.get(user_id)
        if user:
            user.is_active = True
            db.session.commit()
            return True
        return False