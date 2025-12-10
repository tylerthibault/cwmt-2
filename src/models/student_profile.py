"""
StudentProfile model - THIN model following constitutional principles
Contains ONLY database schema and simple serialization
"""
from src.models import db
from src.models.base_model import BaseModel


class StudentProfile(BaseModel):
    """
    Student profile - extends User with student-specific data.
    
    One-to-one relationship with User.
    Contains ONLY student-specific fields, NO business logic.
    """
    __tablename__ = 'student_profiles'
    
    # Foreign key to User (one-to-one)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False, index=True)
    
    # Student-specific fields
    student_number = db.Column(db.String(50), unique=True, nullable=True, index=True)
    overall_score = db.Column(db.Float, default=0.0)
    grade_level = db.Column(db.String(20), nullable=True)
    emergency_contact_name = db.Column(db.String(100), nullable=True)
    emergency_contact_phone = db.Column(db.String(20), nullable=True)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('student_profile', uselist=False), overlaps="student_profile")
    course_enrollments = db.relationship('CourseEnrollment', back_populates='student', cascade='all, delete-orphan')
    
    def to_dict(self):
        """
        Serialize student profile to dictionary.
        Simple serialization only - NO business logic.
        
        Returns:
            dict: Student profile data as dictionary
        """
        data = super().to_dict()
        data.update({
            'user_id': self.user_id,
            'student_number': self.student_number,
            'overall_score': self.overall_score,
            'grade_level': self.grade_level,
            'emergency_contact_name': self.emergency_contact_name,
            'emergency_contact_phone': self.emergency_contact_phone
        })
        return data
    
    def __repr__(self):
        """String representation"""
        return f'<StudentProfile user_id={self.user_id} student_number={self.student_number}>'
