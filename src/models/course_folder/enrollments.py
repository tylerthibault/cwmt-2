from datetime import datetime
from src.models.main import db, CRUDMixin


class Enrollment(db.Model, CRUDMixin):
    """Enrollment model linking students to course instances."""
    
    __tablename__ = 'enrollments'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign Keys
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False, index=True)
    course_instance_id = db.Column(db.Integer, db.ForeignKey('course_instances.id'), nullable=False, index=True)
    
    # Enrollment Information
    enrollment_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    status = db.Column(db.String(50), nullable=False, default='enrolled', index=True)
    completion_date = db.Column(db.DateTime, nullable=True)
    
    # Unenrollment Request Fields
    unenrollment_requested = db.Column(db.Boolean, default=False, nullable=False)
    unenrollment_reason = db.Column(db.Text, nullable=True)
    unenrollment_requested_at = db.Column(db.DateTime, nullable=True)
    refund_percentage = db.Column(db.Integer, default=80, nullable=False)  # Default 80% refund (20% retention)
    unenrollment_processed_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    unenrollment_processed_at = db.Column(db.DateTime, nullable=True)
    unenrollment_admin_notes = db.Column(db.Text, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    student = db.relationship('Student', backref=db.backref('enrollments', lazy='dynamic'))
    course_instance = db.relationship('CourseInstance', backref=db.backref('enrollments', lazy='dynamic'))
    processor = db.relationship('User', foreign_keys=[unenrollment_processed_by], backref='processed_unenrollments', lazy=True)
    
    # Unique constraint - student can only enroll once per course instance
    __table_args__ = (
        db.UniqueConstraint('student_id', 'course_instance_id', name='unique_student_course_enrollment'),
    )
    
    def __init__(self, student_id, course_instance_id, **kwargs):
        """Initialize enrollment."""
        super(Enrollment, self).__init__(**kwargs)
        self.student_id = student_id
        self.course_instance_id = course_instance_id
    
    def __repr__(self):
        return f'<Enrollment {self.id} - Student {self.student_id} - Course {self.course_instance_id} - {self.status}>'
    
    @classmethod
    def get_by_student(cls, student_id):
        """Get all enrollments for a specific student."""
        return cls.query.filter_by(student_id=student_id).order_by(cls.enrollment_date.desc()).all()
    
    @classmethod
    def get_by_course_instance(cls, course_instance_id):
        """Get all enrollments for a specific course instance."""
        return cls.query.filter_by(course_instance_id=course_instance_id).order_by(cls.enrollment_date.asc()).all()
    
    @classmethod
    def get_by_status(cls, status):
        """Get all enrollments with a specific status."""
        return cls.query.filter_by(status=status).order_by(cls.enrollment_date.desc()).all()
    
    @classmethod
    def get_active_enrollments_by_student(cls, student_id):
        """Get all active enrollments for a specific student."""
        return cls.query.filter_by(student_id=student_id, status='enrolled').order_by(cls.enrollment_date.desc()).all()
    
    @classmethod
    def enrollment_exists(cls, student_id, course_instance_id):
        """Check if an enrollment already exists for this student and course."""
        return cls.query.filter_by(student_id=student_id, course_instance_id=course_instance_id).count() > 0
    
    @classmethod
    def get_enrollment(cls, student_id, course_instance_id):
        """Get specific enrollment for student and course."""
        return cls.query.filter_by(student_id=student_id, course_instance_id=course_instance_id).first()
    
    @classmethod
    def count_enrollments_for_course(cls, course_instance_id):
        """Count total enrollments for a course instance."""
        return cls.query.filter_by(course_instance_id=course_instance_id).count()
    
    @classmethod
    def count_active_enrollments_for_course(cls, course_instance_id):
        """Count active enrollments for a course instance."""
        return cls.query.filter_by(course_instance_id=course_instance_id, status='enrolled').count()
    
    def update_status(self, new_status):
        """Update enrollment status."""
        self.status = new_status
        if new_status in ['completed', 'dropped', 'canceled']:
            self.completion_date = datetime.utcnow()
        self.save()
    
    def mark_completed(self):
        """Mark enrollment as completed."""
        self.update_status('completed')
    
    def drop(self):
        """Mark enrollment as dropped."""
        self.update_status('dropped')
    
    def cancel(self):
        """Mark enrollment as canceled."""
        self.update_status('canceled')
    
    def is_active(self):
        """Check if enrollment is active."""
        return self.status == 'enrolled'
    
    def is_completed(self):
        """Check if enrollment is completed."""
        return self.status == 'completed'
    
    def get_payment(self):
        """Get the payment associated with this enrollment."""
        from ..stripe.payments import Payment
        return Payment.query.filter_by(enrollment_id=self.id).first()
    
    def has_payment(self):
        """Check if this enrollment has an associated payment."""
        return self.get_payment() is not None
    
    def request_unenrollment(self, reason='', refund_percentage=80):
        """Request unenrollment from this course."""
        if self.status != 'enrolled':
            raise ValueError(f'Cannot request unenrollment for {self.status} enrollment')
        if self.unenrollment_requested:
            raise ValueError('Unenrollment already requested')
        
        self.unenrollment_requested = True
        self.unenrollment_reason = reason
        self.unenrollment_requested_at = datetime.utcnow()
        self.refund_percentage = refund_percentage
        self.save()
    
    def approve_unenrollment(self, admin_user_id, admin_notes=''):
        """Approve the unenrollment request."""
        if not self.unenrollment_requested:
            raise ValueError('No unenrollment request to approve')
        
        self.status = 'dropped'
        self.completion_date = datetime.utcnow()
        self.unenrollment_processed_by = admin_user_id
        self.unenrollment_processed_at = datetime.utcnow()
        self.unenrollment_admin_notes = admin_notes
        self.save()
    
    def deny_unenrollment(self, admin_user_id, admin_notes=''):
        """Deny the unenrollment request."""
        if not self.unenrollment_requested:
            raise ValueError('No unenrollment request to deny')
        
        self.unenrollment_requested = False
        self.unenrollment_processed_by = admin_user_id
        self.unenrollment_processed_at = datetime.utcnow()
        self.unenrollment_admin_notes = admin_notes
        self.save()
    
    @classmethod
    def get_pending_unenrollments(cls):
        """Get all enrollments with pending unenrollment requests."""
        return cls.query.filter_by(unenrollment_requested=True, status='enrolled').order_by(cls.unenrollment_requested_at.desc()).all()
