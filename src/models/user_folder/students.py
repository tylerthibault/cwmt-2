from datetime import datetime
from src.models.user_folder import users
from src.models.main import db, CRUDMixin


class Student(db.Model, CRUDMixin):
    """Student model with additional student-specific information."""
    
    __tablename__ = 'students'
    
    # Primary Key and Foreign Key to User
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    status_change_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Student Personal Information (can differ from User account holder)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    
    # Student-Specific Information
    phone_number = db.Column(db.String(20))
    student_id = db.Column(db.String(50), unique=True, index=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationship to User
    user = db.relationship('User', backref=db.backref('students', lazy='dynamic'))
    
    def __init__(self, user_id, first_name, last_name, phone_number=None, student_id=None, **kwargs):
        """Initialize student profile."""
        super(Student, self).__init__(**kwargs)
        self.user_id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.phone_number = phone_number
        self.student_id = student_id
    
    @property
    def full_name(self):
        """Return the student's full name."""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def email(self):
        """Return the student's email from User."""
        return self.user.email if self.user else None
    
    def __repr__(self):
        """String representation of the student."""
        return f'<Student {self.student_id or self.id} - {self.full_name}>'

    def change_status(self, is_active: bool):
        """Change the active status of the student and update the status change date."""
        self.is_active = is_active
        self.status_change_date = datetime.utcnow()
        db.session.commit()