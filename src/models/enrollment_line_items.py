"""
Enrollment Line Items model - THIN model following constitutional principles
Contains ONLY database schema and simple serialization
"""
from decimal import Decimal
from src.models import db
from src.models.base_model import BaseModel


class EnrollmentLineItem(BaseModel):
    """
    EnrollmentLineItem database model - THIN model pattern.
    
    Tracks individual payable items for each enrollment.
    Each line item can be paid/refunded independently.
    Captures price snapshot at enrollment time.
    
    Contains ONLY:
    - Database schema (columns, relationships, constraints)
    - Simple serialization methods (to_dict, from_dict)
    
    Does NOT contain:
    - Business logic (belongs in src/logic/payment_logic.py)
    - Validation (belongs in logic layer)
    - Payment calculations (belongs in logic layer)
    """
    __tablename__ = 'enrollment_line_items'
    
    # Foreign keys
    enrollment_id = db.Column(
        db.Integer,
        db.ForeignKey('course_enrollments.id', ondelete='CASCADE'),
        nullable=False
    )
    course_payable_item_id = db.Column(
        db.Integer,
        db.ForeignKey('course_payable_items.id', ondelete='RESTRICT'),
        nullable=False
    )
    
    # Pricing - snapshot at enrollment time
    quantity = db.Column(db.Integer, default=1, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)  # Copied from course_payable_item.price
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)  # unit_price * quantity
    discount_amount = db.Column(db.Numeric(10, 2), default=0.00, nullable=False)
    tax_amount = db.Column(db.Numeric(10, 2), default=0.00, nullable=False)
    total = db.Column(db.Numeric(10, 2), nullable=False)  # subtotal - discount + tax
    
    # Payment status
    status = db.Column(db.String(50), default='pending', nullable=False)  # pending, paid, refunded, partially_refunded
    amount_paid = db.Column(db.Numeric(10, 2), default=0.00, nullable=False)
    amount_refunded = db.Column(db.Numeric(10, 2), default=0.00, nullable=False)
    
    # Relationships
    enrollment = db.relationship('CourseEnrollment', backref='line_items')
    course_payable_item = db.relationship('CoursePayableItem', backref='enrollment_line_items')
    payment_allocations = db.relationship(
        'PaymentAllocation',
        back_populates='enrollment_line_item',
        cascade='all, delete-orphan'
    )
    refunds = db.relationship(
        'Refund',
        back_populates='enrollment_line_item',
        cascade='all, delete-orphan'
    )
    
    # Indexes
    __table_args__ = (
        db.Index('idx_line_item_enrollment_id', 'enrollment_id'),
        db.Index('idx_line_item_status', 'status'),
        db.Index('idx_line_item_enrollment_payable', 'enrollment_id', 'course_payable_item_id'),
    )
    
    def to_dict(self):
        """
        Serialize enrollment line item to dictionary.
        Simple serialization only - NO business logic.
        
        Returns:
            dict: EnrollmentLineItem data as dictionary
        """
        base_dict = super().to_dict()
        base_dict.update({
            'enrollment_id': self.enrollment_id,
            'course_payable_item_id': self.course_payable_item_id,
            'quantity': self.quantity,
            'unit_price': float(self.unit_price) if self.unit_price else 0.0,
            'subtotal': float(self.subtotal) if self.subtotal else 0.0,
            'discount_amount': float(self.discount_amount) if self.discount_amount else 0.0,
            'tax_amount': float(self.tax_amount) if self.tax_amount else 0.0,
            'total': float(self.total) if self.total else 0.0,
            'status': self.status,
            'amount_paid': float(self.amount_paid) if self.amount_paid else 0.0,
            'amount_refunded': float(self.amount_refunded) if self.amount_refunded else 0.0
        })
        return base_dict
    
    def __repr__(self):
        """String representation"""
        return f'<EnrollmentLineItem enrollment={self.enrollment_id} item={self.course_payable_item_id} status={self.status}>'
