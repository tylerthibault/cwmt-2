from datetime import datetime
from sqlalchemy.orm import validates
from jinja2 import Environment, TemplateSyntaxError
from ..main import db, CRUDMixin


class EmailTemplate(db.Model, CRUDMixin):
    """Model for storing customizable email templates."""
    
    __tablename__ = 'email_templates'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Template Identification
    purpose = db.Column(db.String(50), nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    
    # Template Content
    subject_template = db.Column(db.Text, nullable=False)
    body_html_template = db.Column(db.Text, nullable=False)
    body_text_template = db.Column(db.Text, nullable=False)
    
    # Status & Metadata
    is_active = db.Column(db.Boolean, default=False, nullable=False, index=True)
    is_default = db.Column(db.Boolean, default=False, nullable=False)
    
    # Audit Fields
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    creator = db.relationship('User', foreign_keys=[created_by], backref='email_templates_created')
    email_logs = db.relationship('Log', back_populates='template', lazy='dynamic')
    
    # Table constraints
    __table_args__ = (
        db.Index('idx_purpose_active', 'purpose', 'is_active'),
    )
    
    def __repr__(self):
        return f'<EmailTemplate {self.purpose}: {self.name} (Active: {self.is_active})>'
    
    @validates('subject_template', 'body_html_template', 'body_text_template')
    def validate_jinja2_syntax(self, key, value):
        """Validate that template strings have valid Jinja2 syntax."""
        if value:
            env = Environment()
            try:
                env.parse(value)
            except TemplateSyntaxError as e:
                raise ValueError(f"Invalid Jinja2 syntax in {key}: {str(e)}")
        return value
    
    @classmethod
    def get_active_template(cls, purpose):
        """Get the active template for a given purpose.
        
        Args:
            purpose: The email purpose code (e.g., 'password_reset')
            
        Returns:
            EmailTemplate instance or None
        """
        return cls.query.filter_by(purpose=purpose, is_active=True).first()
    
    @classmethod
    def get_templates_by_purpose(cls, purpose):
        """Get all templates for a given purpose.
        
        Args:
            purpose: The email purpose code
            
        Returns:
            List of EmailTemplate instances ordered by active status and creation date
        """
        return cls.query.filter_by(purpose=purpose).order_by(
            cls.is_active.desc(), 
            cls.created_at.desc()
        ).all()
    
    @classmethod
    def deactivate_purpose_templates(cls, purpose, commit=True):
        """Deactivate all templates for a given purpose.
        
        Args:
            purpose: The email purpose code
            commit: Whether to commit changes to database
        """
        templates = cls.query.filter_by(purpose=purpose, is_active=True).all()
        for template in templates:
            template.is_active = False
            db.session.add(template)
        if commit:
            db.session.commit()
    
    def activate(self, commit=True):
        """Activate this template (deactivates other templates for the same purpose).
        
        Args:
            commit: Whether to commit changes to database
            
        Returns:
            self
        """
        # Deactivate all other templates for this purpose
        self.__class__.deactivate_purpose_templates(self.purpose, commit=False)
        
        # Activate this template
        self.is_active = True
        self.updated_at = datetime.utcnow()
        
        if commit:
            db.session.commit()
        
        return self
    
    def deactivate(self, commit=True):
        """Deactivate this template.
        
        Args:
            commit: Whether to commit changes to database
            
        Returns:
            self
        """
        self.is_active = False
        self.updated_at = datetime.utcnow()
        
        if commit:
            db.session.commit()
        
        return self
    
    def can_delete(self):
        """Check if this template can be deleted.
        
        Returns:
            Boolean indicating if deletion is allowed
        """
        # Cannot delete active templates
        if self.is_active:
            return False
        
        # Cannot delete default templates
        if self.is_default:
            return False
        
        return True
    
    def delete(self, commit=True):
        """Delete this template (only if allowed).
        
        Args:
            commit: Whether to commit changes to database
            
        Returns:
            self
            
        Raises:
            ValueError: If template cannot be deleted
        """
        if not self.can_delete():
            if self.is_active:
                raise ValueError("Cannot delete an active template. Deactivate it first.")
            if self.is_default:
                raise ValueError("Cannot delete a default template.")
        
        return super().delete(commit=commit)
    
    def render_subject(self, context):
        """Render the subject template with provided context.
        
        Args:
            context: Dictionary of variables to render template with
            
        Returns:
            Rendered subject string
        """
        env = Environment()
        template = env.from_string(self.subject_template)
        return template.render(**context)
    
    def render_html_body(self, context):
        """Render the HTML body template with provided context.
        
        Args:
            context: Dictionary of variables to render template with
            
        Returns:
            Rendered HTML string
        """
        env = Environment()
        template = env.from_string(self.body_html_template)
        return template.render(**context)
    
    def render_text_body(self, context):
        """Render the plain text body template with provided context.
        
        Args:
            context: Dictionary of variables to render template with
            
        Returns:
            Rendered plain text string
        """
        env = Environment()
        template = env.from_string(self.body_text_template)
        return template.render(**context)
    
    def render_all(self, context):
        """Render all template parts with provided context.
        
        Args:
            context: Dictionary of variables to render template with
            
        Returns:
            Dictionary with 'subject', 'html_body', 'text_body' keys
        """
        return {
            'subject': self.render_subject(context),
            'html_body': self.render_html_body(context),
            'text_body': self.render_text_body(context)
        }
    
    def to_dict(self):
        """Convert template to dictionary representation.
        
        Returns:
            Dictionary with template data
        """
        return {
            'id': self.id,
            'purpose': self.purpose,
            'name': self.name,
            'subject_template': self.subject_template,
            'body_html_template': self.body_html_template,
            'body_text_template': self.body_text_template,
            'is_active': self.is_active,
            'is_default': self.is_default,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'can_delete': self.can_delete()
        }
