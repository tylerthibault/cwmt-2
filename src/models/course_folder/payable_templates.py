from datetime import datetime
from ..main import db, CRUDMixin


class PayableTemplate(db.Model, CRUDMixin):
    """Payable template model for defining payment requirements for courses."""
    
    __tablename__ = 'payable_templates'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Payable Information
    name = db.Column(db.String(100), nullable=False, index=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)  # Decimal for currency
    description = db.Column(db.String(255), nullable=True, index=True)
    is_required = db.Column(db.Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __init__(self, name, amount, description, is_required=True, **kwargs):
        """Initialize payable template."""
        super(PayableTemplate, self).__init__(**kwargs)
        self.name = name
        self.amount = amount
        self.description = description
        self.is_required = is_required
    
    def __repr__(self):
        return f'<PayableTemplate {self.description} - ${self.amount}>'
    
    @classmethod
    def get_required_templates(cls):
        """Get all required payable templates."""
        return cls.query.filter_by(is_required=True).all()
    
    @classmethod
    def get_optional_templates(cls):
        """Get all optional payable templates."""
        return cls.query.filter_by(is_required=False).all()
