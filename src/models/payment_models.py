"""
Payment models - THIN models following constitutional principles
Contains ONLY database schema and simple serialization
"""
from decimal import Decimal
from src.models import db
from src.models.base_model import BaseModel


class Payment(BaseModel):
    """
    Payment database model - THIN model pattern.
    
    Tracks all payments made for enrollments.
    Can be allocated across multiple line items.
    Supports Stripe, cash, check, and other payment methods.
    
    Contains ONLY:
    - Database schema (columns, relationships, constraints)
    - Simple serialization methods (to_dict, from_dict)
    
    Does NOT contain:
    - Business logic (belongs in src/logic/payment_logic.py)
    - Validation (belongs in logic layer)
    - Payment processing (belongs in logic layer)
    """
    __tablename__ = 'payments'
    
    # Foreign keys
    enrollment_id = db.Column(
        db.Integer,
        db.ForeignKey('course_enrollments.id', ondelete='CASCADE'),
        nullable=False
    )
    processed_by_user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='RESTRICT'),
        nullable=False
    )
    
    # Payment details
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)  # stripe, cash, check, other
    status = db.Column(db.String(50), default='pending', nullable=False)  # pending, completed, failed
    payment_date = db.Column(db.DateTime, nullable=False)
    
    # Stripe integration
    stripe_payment_intent_id = db.Column(db.String(255), unique=True, nullable=True)
    stripe_charge_id = db.Column(db.String(255), nullable=True)
    
    # Additional info
    notes = db.Column(db.Text, nullable=True)
    
    # Relationships
    enrollment = db.relationship('CourseEnrollment', backref='payments')
    processed_by = db.relationship('User', backref='processed_payments')
    allocations = db.relationship(
        'PaymentAllocation',
        back_populates='payment',
        cascade='all, delete-orphan'
    )
    refunds = db.relationship(
        'Refund',
        back_populates='original_payment',
        cascade='all, delete-orphan',
        foreign_keys='Refund.original_payment_id'
    )
    
    # Indexes
    __table_args__ = (
        db.Index('idx_payment_enrollment_id', 'enrollment_id'),
        db.Index('idx_payment_status', 'status'),
        db.Index('idx_payment_date', 'payment_date'),
        db.Index('idx_payment_stripe_intent', 'stripe_payment_intent_id'),
    )
    
    def to_dict(self):
        """
        Serialize payment to dictionary.
        Simple serialization only - NO business logic.
        
        Returns:
            dict: Payment data as dictionary
        """
        base_dict = super().to_dict()
        base_dict.update({
            'enrollment_id': self.enrollment_id,
            'processed_by_user_id': self.processed_by_user_id,
            'amount': float(self.amount) if self.amount else 0.0,
            'payment_method': self.payment_method,
            'status': self.status,
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'stripe_payment_intent_id': self.stripe_payment_intent_id,
            'stripe_charge_id': self.stripe_charge_id,
            'notes': self.notes
        })
        return base_dict
    
    def __repr__(self):
        """String representation"""
        return f'<Payment enrollment={self.enrollment_id} amount=${self.amount} status={self.status}>'


class PaymentAllocation(BaseModel):
    """
    PaymentAllocation database model - THIN model pattern.
    
    Tracks how payments are allocated to specific line items.
    Enables granular refunds per line item.
    
    Contains ONLY:
    - Database schema (columns, relationships, constraints)
    - Simple serialization methods (to_dict, from_dict)
    
    Does NOT contain:
    - Business logic (belongs in src/logic/payment_logic.py)
    - Validation (belongs in logic layer)
    """
    __tablename__ = 'payment_allocations'
    
    # Foreign keys
    payment_id = db.Column(
        db.Integer,
        db.ForeignKey('payments.id', ondelete='CASCADE'),
        nullable=False
    )
    enrollment_line_item_id = db.Column(
        db.Integer,
        db.ForeignKey('enrollment_line_items.id', ondelete='CASCADE'),
        nullable=False
    )
    
    # Allocation details
    amount_applied = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Relationships
    payment = db.relationship('Payment', back_populates='allocations')
    enrollment_line_item = db.relationship('EnrollmentLineItem', back_populates='payment_allocations')
    
    # Indexes and constraints
    __table_args__ = (
        db.Index('idx_payment_allocation_payment_id', 'payment_id'),
        db.Index('idx_payment_allocation_line_item_id', 'enrollment_line_item_id'),
        db.UniqueConstraint('payment_id', 'enrollment_line_item_id', name='uq_payment_line_item'),
    )
    
    def to_dict(self):
        """
        Serialize payment allocation to dictionary.
        Simple serialization only - NO business logic.
        
        Returns:
            dict: PaymentAllocation data as dictionary
        """
        base_dict = super().to_dict()
        base_dict.update({
            'payment_id': self.payment_id,
            'enrollment_line_item_id': self.enrollment_line_item_id,
            'amount_applied': float(self.amount_applied) if self.amount_applied else 0.0
        })
        return base_dict
    
    def __repr__(self):
        """String representation"""
        return f'<PaymentAllocation payment={self.payment_id} line_item={self.enrollment_line_item_id} amount=${self.amount_applied}>'


class Refund(BaseModel):
    """
    Refund database model - THIN model pattern.
    
    Tracks refunds for specific line items.
    Links back to original payment for audit trail.
    
    Contains ONLY:
    - Database schema (columns, relationships, constraints)
    - Simple serialization methods (to_dict, from_dict)
    
    Does NOT contain:
    - Business logic (belongs in src/logic/payment_logic.py)
    - Validation (belongs in logic layer)
    - Refund processing (belongs in logic layer)
    """
    __tablename__ = 'refunds'
    
    # Foreign keys
    original_payment_id = db.Column(
        db.Integer,
        db.ForeignKey('payments.id', ondelete='RESTRICT'),
        nullable=False
    )
    enrollment_line_item_id = db.Column(
        db.Integer,
        db.ForeignKey('enrollment_line_items.id', ondelete='CASCADE'),
        nullable=False
    )
    processed_by_user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='RESTRICT'),
        nullable=False
    )
    
    # Refund details
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    refund_method = db.Column(db.String(50), nullable=False)  # stripe, cash, check
    refund_date = db.Column(db.DateTime, nullable=False)
    reason = db.Column(db.Text, nullable=True)
    
    # Stripe integration
    stripe_refund_id = db.Column(db.String(255), unique=True, nullable=True)
    
    # Relationships
    original_payment = db.relationship('Payment', back_populates='refunds', foreign_keys=[original_payment_id])
    enrollment_line_item = db.relationship('EnrollmentLineItem', back_populates='refunds')
    processed_by = db.relationship('User', backref='processed_refunds')
    
    # Indexes
    __table_args__ = (
        db.Index('idx_refund_original_payment_id', 'original_payment_id'),
        db.Index('idx_refund_line_item_id', 'enrollment_line_item_id'),
        db.Index('idx_refund_date', 'refund_date'),
        db.Index('idx_refund_stripe_id', 'stripe_refund_id'),
    )
    
    def to_dict(self):
        """
        Serialize refund to dictionary.
        Simple serialization only - NO business logic.
        
        Returns:
            dict: Refund data as dictionary
        """
        base_dict = super().to_dict()
        base_dict.update({
            'original_payment_id': self.original_payment_id,
            'enrollment_line_item_id': self.enrollment_line_item_id,
            'processed_by_user_id': self.processed_by_user_id,
            'amount': float(self.amount) if self.amount else 0.0,
            'refund_method': self.refund_method,
            'refund_date': self.refund_date.isoformat() if self.refund_date else None,
            'reason': self.reason,
            'stripe_refund_id': self.stripe_refund_id
        })
        return base_dict
    
    def __repr__(self):
        """String representation"""
        return f'<Refund line_item={self.enrollment_line_item_id} amount=${self.amount} method={self.refund_method}>'
