"""
Email Action model - Predefined email actions that can be triggered in code.
Thin model following constitutional principles.
"""
from src.models.base_model import BaseModel
from src.models import db


class EmailAction(BaseModel):
    """
    Predefined email actions (e.g., password_reset, welcome_email).
    Admin users can assign templates to these actions, but cannot create new actions.
    Actions are created via seed data and referenced in code.
    """
    __tablename__ = 'email_actions'
    
    # Unique identifier used in code (e.g., 'password_reset', 'welcome_email')
    action_key = db.Column(db.String(100), unique=True, nullable=False, index=True)
    
    # Human-readable name for display in admin UI
    name = db.Column(db.String(200), nullable=False)
    
    # Description of when this action is triggered
    description = db.Column(db.Text, nullable=True)
    
    # Available template variables (JSON string for display purposes)
    # e.g., "{{user_name}}, {{reset_link}}, {{expiry_time}}"
    available_variables = db.Column(db.Text, nullable=True)
    
    # Foreign key to the assigned template (nullable - action may not have template)
    template_id = db.Column(db.Integer, db.ForeignKey('email_templates.id'), nullable=True)
    
    # Relationship to email template
    template = db.relationship('EmailTemplate', back_populates='actions', foreign_keys=[template_id])
    
    def to_dict(self):
        """Serialize to dictionary"""
        base_dict = super().to_dict()
        base_dict.update({
            'action_key': self.action_key,
            'name': self.name,
            'description': self.description,
            'available_variables': self.available_variables,
            'template_id': self.template_id,
            'template': self.template.to_dict() if self.template else None
        })
        return base_dict
