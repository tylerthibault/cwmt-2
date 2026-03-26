"""
User model - THIN model following constitutional principles
Contains ONLY database schema and simple serialization
"""
from sqlalchemy import event
from src.models import db
from src.models.base_model import BaseModel
from src.utils.encryption import EncryptedType, compute_search_hash


class User(BaseModel):
    """
    User database model - THIN model pattern.

    PII fields (email, username, first_name, last_name) are stored encrypted
    at rest using Fernet symmetric encryption.  Searchable fields (email,
    username) additionally maintain an HMAC-SHA256 blind-index column so that
    exact-match lookups continue to work without exposing plaintext in the DB.

    Contains ONLY:
    - Database schema (columns, relationships, constraints)
    - Simple serialization methods (to_dict, from_dict)

    Does NOT contain:
    - Business logic (belongs in src/logic/user_logic.py)
    - Validation (belongs in logic layer)
    - Complex calculations (belongs in logic layer)
    """
    __tablename__ = 'users'

    # PII fields stored encrypted at rest
    email = db.Column(EncryptedType(), unique=False, nullable=False)
    username = db.Column(EncryptedType(), unique=False, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(EncryptedType(), nullable=True)
    last_name = db.Column(EncryptedType(), nullable=True)

    # Blind-index columns used for exact-match lookups on encrypted fields.
    # Indexed for query performance; unique constraint enforced here instead of
    # on the encrypted column itself.
    email_search_hash = db.Column(db.String(64), unique=True, nullable=True, index=True)
    username_search_hash = db.Column(db.String(64), unique=True, nullable=True, index=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    email_confirmed = db.Column(db.Boolean, default=False, nullable=False)
    email_confirmed_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    roles = db.relationship('UserHasRoles', back_populates='user', cascade='all, delete-orphan', overlaps="role_list,users_list")
    role_list = db.relationship('Role', secondary='user_has_roles', backref='users_list', overlaps="roles")
    logbooks = db.relationship('Logbook', back_populates='user', cascade='all, delete-orphan')
    
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
        Get user by email using the blind-index search hash.

        Args:
            email (str): Email of the user

        Returns:
            User: The user instance or None if not found
        """
        return cls.query.filter_by(email_search_hash=compute_search_hash(email)).first()

    @classmethod
    def get_by_username(cls, username):
        """
        Get user by username using the blind-index search hash.

        Args:
            username (str): Username of the user

        Returns:
            User: The user instance or None if not found
        """
        return cls.query.filter_by(username_search_hash=compute_search_hash(username)).first()
    
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


# ---------------------------------------------------------------------------
# SQLAlchemy event listeners — automatically keep blind-index hash columns in
# sync with their plaintext counterparts before any INSERT or UPDATE.
# ---------------------------------------------------------------------------

@event.listens_for(User, 'before_insert')
@event.listens_for(User, 'before_update')
def _sync_search_hashes(mapper, connection, target):  # noqa: N802
    """Recompute HMAC blind-index hashes whenever a User is saved."""
    if target.email is not None:
        target.email_search_hash = compute_search_hash(target.email)
    if target.username is not None:
        target.username_search_hash = compute_search_hash(target.username)