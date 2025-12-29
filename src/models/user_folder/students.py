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
    
    # Guest Account Tracking
    created_by_student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=True, index=True)
    relationship = db.Column(db.String(50))  # child, spouse, parent, sibling, friend, other
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationship to User
    user = db.relationship('User', backref=db.backref('students', lazy='dynamic'))
    
    # Self-referential relationship for guest accounts
    created_by = db.relationship('Student', remote_side=[id], backref='guest_students', foreign_keys=[created_by_student_id])
    
    def __init__(self, user_id, first_name, last_name, phone_number=None, student_id=None, created_by_student_id=None, relationship=None, **kwargs):
        """Initialize student profile."""
        super(Student, self).__init__(**kwargs)
        self.user_id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.phone_number = phone_number
        self.student_id = student_id
        self.created_by_student_id = created_by_student_id
        self.relationship = relationship

    @property
    def enrollments(self):
        """Return all enrollments for this student."""
        from src.models.course_folder.enrollments import Enrollment
        return Enrollment.query.filter_by(student_id=self.id).all()
    
    @property
    def is_guest_account(self):
        """Check if this is a guest account created by another student."""
        return self.created_by_student_id is not None
    
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