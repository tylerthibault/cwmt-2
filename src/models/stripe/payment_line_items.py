from datetime import datetime
from src.models.main import db, CRUDMixin


class PaymentLineItem(db.Model, CRUDMixin):
    """Payment line item model for itemized payment details."""
    
    __tablename__ = 'payment_line_items'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign Keys
    payment_id = db.Column(db.Integer, db.ForeignKey('payments.id'), nullable=False, index=True)
    payable_template_id = db.Column(db.Integer, db.ForeignKey('payable_templates.id'), nullable=False, index=True)
    
    # Line Item Details
    cost_of_item = db.Column(db.Integer, nullable=False)  # Amount in cents
    quantity = db.Column(db.Integer, nullable=False, default=1)
    amount_refunded = db.Column(db.Integer, nullable=False, default=0)  # Amount in cents
    status = db.Column(db.String(50), nullable=False, default='active', index=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    # Note: 'payment' relationship is provided via backref from Payment model
    payable_template = db.relationship('PayableTemplate', backref=db.backref('payment_line_items', lazy='dynamic'))
    
    def __init__(self, payment_id, payable_template_id, cost_of_item, quantity=1, **kwargs):
        """Initialize payment line item."""
        super(PaymentLineItem, self).__init__(**kwargs)
        self.payment_id = payment_id
        self.payable_template_id = payable_template_id
        self.cost_of_item = cost_of_item
        self.quantity = quantity
    
    def __repr__(self):
        return f'<PaymentLineItem {self.id} - ${self.cost_of_item/100:.2f} x {self.quantity}>'
    
    @classmethod
    def get_by_payment(cls, payment_id):
        """Get all line items for a specific payment."""
        return cls.query.filter_by(payment_id=payment_id).all()
    
    @classmethod
    def get_by_payable_template(cls, payable_template_id):
        """Get all line items for a specific payable template."""
        return cls.query.filter_by(payable_template_id=payable_template_id).order_by(cls.created_at.desc()).all()
    
    @classmethod
    def get_by_status(cls, status):
        """Get all line items with a specific status."""
        return cls.query.filter_by(status=status).order_by(cls.created_at.desc()).all()
    
    def get_total_cost(self):
        """Get total cost for this line item (cost * quantity) in cents."""
        return self.cost_of_item * self.quantity
    
    def add_refund(self, refund_amount):
        """Add refund amount to this line item."""
        self.amount_refunded += refund_amount
        total_cost = self.get_total_cost()
        if self.amount_refunded >= total_cost:
            self.status = 'refunded'
        else:
            self.status = 'partially_refunded'
        self.save()
    
    def get_cost_in_dollars(self):
        """Get cost per item in dollars (converts from cents)."""
        return self.cost_of_item / 100
    
    def get_total_in_dollars(self):
        """Get total cost in dollars (cost * quantity, converted from cents)."""
        return self.get_total_cost() / 100
    
    def get_refunded_amount_in_dollars(self):
        """Get refunded amount in dollars (converts from cents)."""
        return self.amount_refunded / 100
    
    def is_fully_refunded(self):
        """Check if this line item is fully refunded."""
        return self.status == 'refunded'
    
    def is_partially_refunded(self):
        """Check if this line item is partially refunded."""
        return self.status == 'partially_refunded'
    
    def get_remaining_amount(self):
        """Get the remaining amount (total - refunded) in cents."""
        return self.get_total_cost() - self.amount_refunded
    
    def get_remaining_amount_in_dollars(self):
        """Get the remaining amount in dollars."""
        return self.get_remaining_amount() / 100
