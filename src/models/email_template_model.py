"""
Email Template model - Admin-created email templates for system actions.
Thin model following constitutional principles.
"""
from src.models.base_model import BaseModel
from src.models import db


class EmailTemplate(BaseModel):
    """
    Email templates created by admin users.
    Can be assigned to predefined email actions.
    Supports both HTML and plain text versions.
    """
    __tablename__ = 'email_templates'
    
    # Template name (for admin reference)
    name = db.Column(db.String(200), nullable=False)
    
    # Email subject line (supports template variables)
    subject = db.Column(db.String(500), nullable=False)
    
    # MJML source (optional - if provided, body_html is auto-generated)
    body_mjml = db.Column(db.Text, nullable=True)
    
    # HTML version of email body (supports template variables)
    # Auto-generated from body_mjml if MJML is used
    body_html = db.Column(db.Text, nullable=True)
    
    # Plain text version of email body (supports template variables)
    body_text = db.Column(db.Text, nullable=False)
    
    # Admin notes about this template
    description = db.Column(db.Text, nullable=True)
    
    # Active status
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Relationship to email actions (one template can be assigned to multiple actions)
    actions = db.relationship('EmailAction', back_populates='template', foreign_keys='EmailAction.template_id')
    
    def to_dict(self):
        """Serialize to dictionary"""
        base_dict = super().to_dict()
        base_dict.update({
            'name': self.name,
            'subject': self.subject,
            'body_mjml': self.body_mjml,
            'body_html': self.body_html,
            'body_text': self.body_text,
            'description': self.description,
            'is_active': self.is_active,
            'action_count': len(self.actions) if self.actions else 0
        })
        return base_dict
