from datetime import datetime
from flask_bcrypt import generate_password_hash, check_password_hash
from ..main import db, CRUDMixin
from flask import flash
from src.models.user_folder import students, instructors, admins, superusers

class User(db.Model, CRUDMixin):
    """Base User model for all user types (students, instructors, admin, superusers)."""
    
    __tablename__ = 'users'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # User Identification
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Personal Information
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), nullable=True)
    
    # Status
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login = db.Column(db.DateTime)
    
    def __init__(self, email, password, first_name, last_name, **kwargs):
        """Initialize user with hashed password."""
        super(User, self).__init__(**kwargs)
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.set_password(password)
    

    @classmethod
    def create(cls, **data):
        """Create a new user instance and save to the database."""
        # check to see if user with email already exists
        existing_user = cls.query.filter_by(email=data.get('email')).first()
        if existing_user:
            flash('User with this email already exists.', 'warning')
            return existing_user
        user = cls(**data)
        user.save()
        return user

    def set_password(self, password):
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        """Verify a password against the hash."""
        return check_password_hash(self.password_hash, password)
    
    def update_last_login(self):
        """Update the last login timestamp."""
        self.last_login = datetime.utcnow()
        self.save()
    
    @property
    def full_name(self):
        """Return the user's full name."""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def is_student(self):
        """Check if user has student role."""
        return self.has_role_by_name('student')
    
    @property
    def is_instructor(self):
        """Check if user has instructor role."""
        return self.has_role_by_name('instructor')
    
    @property
    def is_admin(self):
        """Check if user has admin role."""
        return self.has_role_by_name('admin')
    
    @property
    def is_superuser(self):
        """Check if user has superuser role."""
        return self.has_role_by_name('superuser')
    
    def has_role_by_name(self, role_name):
        """Check if user has a role by querying the corresponding table."""
        if role_name == 'student':
            return students.Student.query.filter_by(user_id=self.id).first() is not None
        elif role_name == 'instructor':
            return instructors.Instructor.query.filter_by(user_id=self.id).first() is not None
        elif role_name == 'admin':
            return admins.Admin.query.filter_by(user_id=self.id).first() is not None
        elif role_name == 'superuser':
            return superusers.Superuser.query.filter_by(user_id=self.id).first() is not None
        else:
            return False

    def get_roles(self):
        """Get all roles assigned to this user."""
        list_of_roles = []
        if self.is_superuser:
            list_of_roles.append('superuser')
        if self.is_admin:
            list_of_roles.append('admin')
        if self.is_instructor:
            list_of_roles.append('instructor')
        if self.is_student:
            list_of_roles.append('student')
        return list_of_roles
    
    def __repr__(self):
        """String representation of the user."""
        roles = ', '.join(self.get_roles()) if self.get_roles() else 'no roles'
        return f'<User {self.email} ({roles})>'
