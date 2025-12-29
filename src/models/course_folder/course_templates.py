from datetime import datetime
from ..main import db, CRUDMixin


# Association table 
course_payables = db.Table('course_payables',
    db.Column('course_template_id', db.Integer, db.ForeignKey('course_templates.id'), primary_key=True),
    db.Column('payable_template_id', db.Integer, db.ForeignKey('payable_templates.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow)
)

class CourseTemplate(db.Model, CRUDMixin):
    """Course template model for defining types of courses."""
    
    __tablename__ = 'course_templates'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Course Information
    name = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    experience_level = db.Column(db.String(50), nullable=False)  # e.g., Beginner, Intermediate, Advanced
    duration_days = db.Column(db.Integer, nullable=False)  # Duration in days
    max_students = db.Column(db.Integer, nullable=False)  # Maximum number of students allowed
    color = db.Column(db.String(7), nullable=False, default='#0d6efd')  # Hex color code for calendar display
    
    # Status
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Many-to-many relationship
    payable_templates = db.relationship('PayableTemplate',
                                       secondary=course_payables,
                                       backref=db.backref('course_templates', lazy='dynamic'),
                                       lazy='dynamic')
    
    def __init__(self, name, experience_level, duration_days, max_students, color='#0d6efd', **kwargs):
        """Initialize course template."""
        super(CourseTemplate, self).__init__(**kwargs)
        self.name = name
        self.experience_level = experience_level
        self.duration_days = duration_days
        self.max_students = max_students
        self.color = color
    
    def __repr__(self):
        return f'<CourseTemplate {self.name} ({self.experience_level})>'
    
    @classmethod
    def get_active_templates(cls):
        """Get all active course templates."""
        return cls.query.filter_by(is_active=True).all()
    
    @classmethod
    def get_by_experience_level(cls, level):
        """Get all templates for a specific experience level."""
        return cls.query.filter_by(experience_level=level, is_active=True).all()
