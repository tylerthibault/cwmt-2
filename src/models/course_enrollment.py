"""
CourseEnrollment model - THIN model following constitutional principles
Contains ONLY database schema and simple serialization
"""
from src.models import db
from src.models.base_model import BaseModel


class CourseEnrollment(BaseModel):
    """
    Course enrollment - tracks student enrollment in specific courses.
    
    Contains course-specific student data like equipment, scores, attendance.
    THIN model - NO business logic.
    """
    __tablename__ = 'course_enrollments'
    
    # Foreign keys
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id'), nullable=False, index=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False, index=True)
    
    # Enrollment status
    status = db.Column(db.String(20), default='active', index=True)  # active, completed, withdrawn, failed
    enrollment_date = db.Column(db.DateTime, nullable=False)
    completion_date = db.Column(db.DateTime, nullable=True)
    
    # Course-specific data
    course_score = db.Column(db.Float, default=0.0)
    attendance_percentage = db.Column(db.Float, default=0.0)
    
    # Equipment/vehicle information
    brings_motorcycle = db.Column(db.Boolean, default=False)
    motorcycle_make = db.Column(db.String(50), nullable=True)
    motorcycle_model = db.Column(db.String(50), nullable=True)
    motorcycle_year = db.Column(db.Integer, nullable=True)
    motorcycle_license_plate = db.Column(db.String(20), nullable=True)
    
    # Additional course-specific notes
    notes = db.Column(db.Text, nullable=True)
    
    # Relationships
    student = db.relationship('StudentProfile', back_populates='course_enrollments')
    course = db.relationship('Course', back_populates='enrollments')
    
    # Unique constraint: student can only enroll once per course
    __table_args__ = (
        db.UniqueConstraint('student_id', 'course_id', name='unique_student_course'),
    )
    
    def to_dict(self):
        """
        Serialize enrollment to dictionary.
        Simple serialization only - NO business logic.
        
        Returns:
            dict: Enrollment data as dictionary
        """
        data = super().to_dict()
        data.update({
            'student_id': self.student_id,
            'course_id': self.course_id,
            'status': self.status,
            'enrollment_date': self.enrollment_date.isoformat() if self.enrollment_date else None,
            'completion_date': self.completion_date.isoformat() if self.completion_date else None,
            'course_score': self.course_score,
            'attendance_percentage': self.attendance_percentage,
            'brings_motorcycle': self.brings_motorcycle,
            'motorcycle_make': self.motorcycle_make,
            'motorcycle_model': self.motorcycle_model,
            'motorcycle_year': self.motorcycle_year,
            'motorcycle_license_plate': self.motorcycle_license_plate,
            'notes': self.notes
        })
        return data
    
    def __repr__(self):
        """String representation"""
        return f'<CourseEnrollment student_id={self.student_id} course_id={self.course_id} status={self.status}>'
