from datetime import datetime
from ..main import db, CRUDMixin


class CourseInstance(db.Model, CRUDMixin):
    """Course instance model for actual scheduled courses based on templates."""
    
    __tablename__ = 'course_instances'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign Key to Course Template
    course_template_id = db.Column(db.Integer, db.ForeignKey('course_templates.id'), nullable=False, index=True)
    
    # Foreign Keys to Instructors (supporting two instructors)
    c1_instructor_id = db.Column(db.Integer, db.ForeignKey('instructors.id'), nullable=True, index=True)
    c2_instructor_id = db.Column(db.Integer, db.ForeignKey('instructors.id'), nullable=True, index=True)
    
    # Schedule Information
    start_date = db.Column(db.Date, nullable=False, index=True)
    start_time = db.Column(db.Time, nullable=False)
    duration_days = db.Column(db.Integer, nullable=False)  # Duration in days
    
    # Location Information
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=False, index=True)
    
    # Tax Information (stored at time of course creation)
    tax_rate = db.Column(db.Numeric(5, 4), nullable=False, default=0.0000)  # Tax rate at time of purchase
    
    # Capacity
    max_students = db.Column(db.Integer, nullable=False)
    
    # Status
    status = db.Column(db.String(50), default='scheduled', nullable=False)  # scheduled, active, completed, cancelled
    
    # Additional Notes
    notes = db.Column(db.Text, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    course_template = db.relationship('CourseTemplate', backref=db.backref('instances', lazy='dynamic'))
    c1_instructor = db.relationship('Instructor', foreign_keys=[c1_instructor_id], backref=db.backref('c1_course_instances', lazy='dynamic'))
    c2_instructor = db.relationship('Instructor', foreign_keys=[c2_instructor_id], backref=db.backref('c2_course_instances', lazy='dynamic'))
    location = db.relationship('Location', backref=db.backref('course_instances', lazy='dynamic'))
    
    def __init__(self, course_template_id, start_date, start_time, duration_days, location_id, max_students, tax_rate=0.0000, **kwargs):
        """Initialize course instance."""
        super(CourseInstance, self).__init__(**kwargs)
        self.course_template_id = course_template_id
        self.start_date = start_date
        self.start_time = start_time
        self.duration_days = duration_days
        self.location_id = location_id
        self.max_students = max_students
        self.tax_rate = tax_rate
    
    def __repr__(self):
        return f'<CourseInstance {self.course_template.name if self.course_template else "Unknown"} on {self.start_date}>'
    
    @classmethod
    def get_by_status(cls, status):
        """Get all course instances with a specific status."""
        return cls.query.filter_by(status=status).all()
    
    @classmethod
    def get_upcoming(cls):
        """Get all upcoming scheduled course instances."""
        return cls.query.filter(
            cls.start_date >= datetime.utcnow().date(),
            cls.status == 'scheduled'
        ).order_by(cls.start_date).all()
    
    @classmethod
    def get_by_c1_instructor(cls, instructor_id):
        """Get all course instances where instructor is c1_instructor."""
        return cls.query.filter_by(c1_instructor_id=instructor_id).order_by(cls.start_date.desc()).all()
    
    @classmethod
    def get_by_c2_instructor(cls, instructor_id):
        """Get all course instances where instructor is c2_instructor."""
        return cls.query.filter_by(c2_instructor_id=instructor_id).order_by(cls.start_date.desc()).all()
    
    @classmethod
    def get_by_instructor(cls, instructor_id):
        """Get all course instances for a specific instructor (either c1 or c2)."""
        return cls.query.filter(
            (cls.c1_instructor_id == instructor_id) | (cls.c2_instructor_id == instructor_id)
        ).order_by(cls.start_date.desc()).all()

    def get_total_tuition(self):
        """Calculate total tuition based on associated payable templates."""
        total = 0.0
        if self.course_template:
            for payable in self.course_template.payable_templates:
                total += float(payable.amount)
        return total
    
    def calculate_pricing(self):
        """Calculate subtotal, tax, and total for this course instance.
        
        Returns:
            tuple: (subtotal, tax_amount, total)
        """
        subtotal = self.get_total_tuition()
        
        # Check if this is a test session - if so, no tax
        if self.course_template and not self.course_template.is_taxable:
            return (subtotal, 0.0, subtotal)
        
        # Calculate tax using the stored tax_rate
        tax_amount = subtotal * float(self.tax_rate)
        total = subtotal + tax_amount
        
        return (subtotal, tax_amount, total)