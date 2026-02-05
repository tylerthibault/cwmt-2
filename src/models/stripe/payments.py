from datetime import datetime
from src.models.main import db, CRUDMixin


class Payment(db.Model, CRUDMixin):
    """Payment model for tracking Stripe payment transactions."""
    
    __tablename__ = 'payments'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign Keys
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False, index=True)
    course_instance_id = db.Column(db.Integer, db.ForeignKey('course_instances.id'), nullable=False, index=True)
    enrollment_id = db.Column(db.Integer, db.ForeignKey('enrollments.id'), nullable=True, index=True)
    
    # Stripe Information
    stripe_payment_intent_id = db.Column(db.String(255), nullable=False, unique=True, index=True)
    stripe_charge_id = db.Column(db.String(255), nullable=True, index=True)
    idempotency_key = db.Column(db.String(255), nullable=False, unique=True, index=True)
    
    # Payment Details
    status = db.Column(db.String(50), nullable=False, default='pending', index=True)
    total_cost = db.Column(db.Integer, nullable=False)  # Amount in cents
    tax_amount = db.Column(db.Integer, nullable=False, default=0)  # Tax amount in cents
    amount_refunded = db.Column(db.Integer, nullable=False, default=0)  # Amount in cents
    currency = db.Column(db.String(3), nullable=False, default='usd')
    
    # Payment Method Info
    payment_method_type = db.Column(db.String(50), nullable=True)
    last4 = db.Column(db.String(4), nullable=True)
    
    # Additional Info
    customer_email = db.Column(db.String(255), nullable=False)
    receipt_url = db.Column(db.String(500), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    student = db.relationship('Student', backref=db.backref('payments', lazy='dynamic'))
    course_instance = db.relationship('CourseInstance', backref=db.backref('payments', lazy='dynamic'))
    enrollment = db.relationship('Enrollment', backref=db.backref('payments', lazy='dynamic'))
    line_items = db.relationship('PaymentLineItem', backref='payment', lazy='dynamic', cascade='all, delete-orphan')
    
    def __init__(self, student_id, course_instance_id, stripe_payment_intent_id, 
                 idempotency_key, total_cost, customer_email, **kwargs):
        """Initialize payment."""
        super(Payment, self).__init__(**kwargs)
        self.student_id = student_id
        self.course_instance_id = course_instance_id
        self.stripe_payment_intent_id = stripe_payment_intent_id
        self.idempotency_key = idempotency_key
        self.total_cost = total_cost
        self.customer_email = customer_email
    
    def __repr__(self):
        return f'<Payment {self.id} - {self.status} - ${self.total_cost/100:.2f}>'
    
    @classmethod
    def get_by_payment_intent_id(cls, payment_intent_id):
        """Get payment by Stripe PaymentIntent ID."""
        return cls.query.filter_by(stripe_payment_intent_id=payment_intent_id).first()
    
    @classmethod
    def get_by_student(cls, student_id):
        """Get all payments for a specific student."""
        return cls.query.filter_by(student_id=student_id).order_by(cls.created_at.desc()).all()
    
    @classmethod
    def get_by_course_instance(cls, course_instance_id):
        """Get all payments for a specific course instance."""
        return cls.query.filter_by(course_instance_id=course_instance_id).order_by(cls.created_at.desc()).all()
    
    @classmethod
    def get_by_status(cls, status):
        """Get all payments with a specific status."""
        return cls.query.filter_by(status=status).order_by(cls.created_at.desc()).all()
    
    def update_status(self, new_status):
        """Update payment status."""
        self.status = new_status
        self.save()
    
    def add_refund(self, refund_amount):
        """Add refund amount to the payment."""
        self.amount_refunded += refund_amount
        if self.amount_refunded >= self.total_cost:
            self.status = 'refunded'
        else:
            self.status = 'partially_refunded'
        self.save()
    
    def is_successful(self):
        """Check if payment was successful."""
        return self.status == 'succeeded'
    
    def is_refunded(self):
        """Check if payment is fully or partially refunded."""
        return self.status in ['refunded', 'partially_refunded']
    
    def get_amount_in_dollars(self):
        """Get total cost in dollars (converts from cents)."""
        return self.total_cost / 100
    
    def get_refunded_amount_in_dollars(self):
        """Get refunded amount in dollars (converts from cents)."""
        return self.amount_refunded / 100

