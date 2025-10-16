"""
Course and CourseTemplate models - THIN models following constitutional principles
Contains ONLY database schema and simple serialization
"""
from datetime import datetime, date, time
from src.models import db
from src.models.base_model import BaseModel


class CourseTemplate(BaseModel):
    """
    CourseTemplate database model - THIN model pattern.
    
    Represents a template/blueprint for courses with reusable configuration.
    
    Contains ONLY:
    - Database schema (columns, relationships, constraints)
    - Simple serialization methods (to_dict, from_dict)
    
    Does NOT contain:
    - Business logic (belongs in src/logic/course_logic.py)
    - Validation (belongs in logic layer)
    - Complex calculations (belongs in logic layer)
    """
    __tablename__ = 'course_templates'
    
    # Template fields
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    duration_days = db.Column(db.Integer, nullable=False)  # Length of course in days
    experience_level = db.Column(db.String(50), nullable=False)  # e.g., 'beginner', 'intermediate', 'advanced'
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Relationships
    courses = db.relationship('Course', back_populates='template', cascade='all, delete-orphan')
    
    def to_dict(self):
        """
        Serialize course template to dictionary.
        Simple serialization only - NO business logic.
        
        Returns:
            dict: CourseTemplate data as dictionary
        """
        base_dict = super().to_dict()
        base_dict.update({
            'name': self.name,
            'description': self.description,
            'duration_days': self.duration_days,
            'experience_level': self.experience_level,
            'is_active': self.is_active,
            'courses_count': len(self.courses) if self.courses else 0
        })
        return base_dict
    
    def __repr__(self):
        """String representation of course template"""
        return f'<CourseTemplate {self.name} ({self.experience_level})>'


class Course(BaseModel):
    """
    Course database model - THIN model pattern.
    
    Represents an instance of a course template scheduled at a specific date/time.
    Each course has 1 student and 2 instructors.
    
    Contains ONLY:
    - Database schema (columns, relationships, constraints)
    - Simple serialization methods (to_dict, from_dict)
    
    Does NOT contain:
    - Business logic (belongs in src/logic/course_logic.py)
    - Validation (belongs in logic layer)
    - Complex calculations (belongs in logic layer)
    """
    __tablename__ = 'courses'
    
    # Course fields
    course_template_id = db.Column(db.Integer, db.ForeignKey('course_templates.id'), nullable=False)
    course_date = db.Column(db.Date, nullable=False)
    course_time = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(50), default='scheduled', nullable=False)  # e.g., 'scheduled', 'in_progress', 'completed', 'cancelled'
    location = db.Column(db.String(255), nullable=True)  # Optional location field
    
    # Student and Instructor relationships (many-to-one with User)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    instructor1_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    instructor2_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Relationships
    template = db.relationship('CourseTemplate', back_populates='courses')
    student = db.relationship('User', foreign_keys=[student_id], backref='enrolled_courses')
    instructor1 = db.relationship('User', foreign_keys=[instructor1_id], backref='courses_as_instructor1')
    instructor2 = db.relationship('User', foreign_keys=[instructor2_id], backref='courses_as_instructor2')
    
    def to_dict(self, include_users=False, include_template=False):
        """
        Serialize course to dictionary.
        Simple serialization only - NO business logic.
        
        Args:
            include_users (bool): Whether to include user details
            include_template (bool): Whether to include template details
            
        Returns:
            dict: Course data as dictionary
        """
        base_dict = super().to_dict()
        base_dict.update({
            'course_template_id': self.course_template_id,
            'course_date': self.course_date.isoformat() if self.course_date else None,
            'course_time': self.course_time.isoformat() if self.course_time else None,
            'status': self.status,
            'student_id': self.student_id,
            'instructor1_id': self.instructor1_id,
            'instructor2_id': self.instructor2_id
        })
        
        if include_template and self.template:
            base_dict['template'] = self.template.to_dict()
        
        if include_users:
            base_dict['student'] = self.student.to_dict() if self.student else None
            base_dict['instructor1'] = self.instructor1.to_dict() if self.instructor1 else None
            base_dict['instructor2'] = self.instructor2.to_dict() if self.instructor2 else None
        
        return base_dict
    
    def __repr__(self):
        """String representation of course"""
        return f'<Course {self.id} - Template: {self.course_template_id} on {self.course_date}>'
