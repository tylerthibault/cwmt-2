from datetime import datetime
from src.models.main import db, CRUDMixin


class StripeWebhookEvent(db.Model, CRUDMixin):
    """Stripe webhook event model for logging all webhook events."""
    
    __tablename__ = 'stripe_webhook_events'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign Keys
    payment_id = db.Column(db.Integer, db.ForeignKey('payments.id'), nullable=True, index=True)
    
    # Event Information
    stripe_event_id = db.Column(db.String(255), nullable=False, unique=True, index=True)
    event_type = db.Column(db.String(100), nullable=False, index=True)
    payload = db.Column(db.Text, nullable=False)  # JSON payload as text
    
    # Processing Status
    processed = db.Column(db.Boolean, nullable=False, default=False, index=True)
    error_message = db.Column(db.Text, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    payment = db.relationship('Payment', backref=db.backref('webhook_events', lazy='dynamic'))
    
    def __init__(self, stripe_event_id, event_type, payload, **kwargs):
        """Initialize webhook event."""
        super(StripeWebhookEvent, self).__init__(**kwargs)
        self.stripe_event_id = stripe_event_id
        self.event_type = event_type
        self.payload = payload
    
    def __repr__(self):
        return f'<StripeWebhookEvent {self.stripe_event_id} - {self.event_type}>'
    
    @classmethod
    def get_by_event_id(cls, event_id):
        """Get webhook event by Stripe event ID."""
        return cls.query.filter_by(stripe_event_id=event_id).first()
    
    @classmethod
    def event_exists(cls, event_id):
        """Check if a webhook event has already been received."""
        return cls.query.filter_by(stripe_event_id=event_id).count() > 0
    
    @classmethod
    def get_unprocessed_events(cls):
        """Get all unprocessed webhook events."""
        return cls.query.filter_by(processed=False).order_by(cls.created_at.asc()).all()
    
    @classmethod
    def get_by_event_type(cls, event_type):
        """Get all webhook events of a specific type."""
        return cls.query.filter_by(event_type=event_type).order_by(cls.created_at.desc()).all()
    
    @classmethod
    def get_by_payment(cls, payment_id):
        """Get all webhook events for a specific payment."""
        return cls.query.filter_by(payment_id=payment_id).order_by(cls.created_at.desc()).all()
    
    @classmethod
    def get_failed_events(cls):
        """Get all webhook events that failed processing."""
        return cls.query.filter(cls.processed == False, cls.error_message != None).order_by(cls.created_at.desc()).all()
    
    def mark_as_processed(self):
        """Mark webhook event as successfully processed."""
        self.processed = True
        self.error_message = None
        self.save()
    
    def mark_as_failed(self, error_message):
        """Mark webhook event as failed with error message."""
        self.processed = False
        self.error_message = error_message
        self.save()
    
    def get_payload_as_dict(self):
        """Get payload as dictionary (parse JSON)."""
        import json
        try:
            return json.loads(self.payload)
        except json.JSONDecodeError as e:
            return {'error': f'Failed to parse payload: {str(e)}'}
    
    def is_processed(self):
        """Check if webhook event has been successfully processed."""
        return self.processed
    
    def has_error(self):
        """Check if webhook event has an error message."""
        return self.error_message is not None and self.error_message != ''
