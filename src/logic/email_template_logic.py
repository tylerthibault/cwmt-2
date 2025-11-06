"""
Business logic for email template management.
Thick logic layer following constitutional principles.
"""
from typing import Dict, List, Optional
from src.models.email_template_model import EmailTemplate
from src.models.email_action_model import EmailAction
from src.models import db
import logging

logger = logging.getLogger(__name__)


class EmailTemplateLogic:
    """Handle email template CRUD operations and action assignments."""
    
    @staticmethod
    def get_all_templates(include_inactive: bool = False) -> List[EmailTemplate]:
        """
        Get all email templates.
        
        Args:
            include_inactive: Whether to include inactive templates
            
        Returns:
            List of EmailTemplate objects
        """
        query = EmailTemplate.query
        if not include_inactive:
            query = query.filter_by(is_active=True)
        return query.order_by(EmailTemplate.name).all()
    
    @staticmethod
    def get_template_by_id(template_id: int) -> Optional[EmailTemplate]:
        """
        Get email template by ID.
        
        Args:
            template_id: Template ID
            
        Returns:
            EmailTemplate object or None
        """
        return EmailTemplate.query.get(template_id)
    
    @staticmethod
    def create_template(data: Dict) -> EmailTemplate:
        """
        Create new email template with validation.
        
        Args:
            data: Dictionary with template data
                - name (required): Template name
                - subject (required): Email subject
                - body_text (required): Plain text body
                - body_html (optional): HTML body
                - description (optional): Admin notes
                - is_active (optional): Active status
                
        Returns:
            Created EmailTemplate object
            
        Raises:
            ValueError: If required fields are missing or invalid
        """
        # Validation
        if not data.get('name'):
            raise ValueError('Template name is required')
        if not data.get('subject'):
            raise ValueError('Email subject is required')
        if not data.get('body_text'):
            raise ValueError('Plain text body is required')
        
        # Check for duplicate names
        existing = EmailTemplate.query.filter_by(name=data['name']).first()
        if existing:
            raise ValueError(f'Template with name "{data["name"]}" already exists')
        
        # Create template
        template = EmailTemplate(
            name=data['name'],
            subject=data['subject'],
            body_text=data['body_text'],
            body_html=data.get('body_html', ''),
            body_mjml=data.get('body_mjml', ''),
            description=data.get('description', ''),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(template)
        db.session.commit()
        
        logger.info(f'Created email template: {template.name} (ID: {template.id})')
        return template
    
    @staticmethod
    def update_template(template_id: int, data: Dict) -> EmailTemplate:
        """
        Update existing email template.
        
        Args:
            template_id: ID of template to update
            data: Dictionary with fields to update
            
        Returns:
            Updated EmailTemplate object
            
        Raises:
            ValueError: If template not found or validation fails
        """
        template = EmailTemplate.query.get(template_id)
        if not template:
            raise ValueError(f'Template with ID {template_id} not found')
        
        # Validate if name is being changed
        if 'name' in data and data['name'] != template.name:
            existing = EmailTemplate.query.filter_by(name=data['name']).first()
            if existing:
                raise ValueError(f'Template with name "{data["name"]}" already exists')
        
        # Validate required fields if provided
        if 'subject' in data and not data['subject']:
            raise ValueError('Email subject cannot be empty')
        if 'body_text' in data and not data['body_text']:
            raise ValueError('Plain text body cannot be empty')
        
        # Update fields
        if 'name' in data:
            template.name = data['name']
        if 'subject' in data:
            template.subject = data['subject']
        if 'body_text' in data:
            template.body_text = data['body_text']
        if 'body_html' in data:
            template.body_html = data['body_html']
        if 'body_mjml' in data:
            template.body_mjml = data['body_mjml']
        if 'description' in data:
            template.description = data['description']
        if 'is_active' in data:
            template.is_active = data['is_active']
        
        db.session.commit()
        
        logger.info(f'Updated email template: {template.name} (ID: {template.id})')
        return template
    
    @staticmethod
    def delete_template(template_id: int) -> bool:
        """
        Delete email template (soft delete by setting inactive).
        
        Args:
            template_id: ID of template to delete
            
        Returns:
            True if successful
            
        Raises:
            ValueError: If template not found or still assigned to actions
        """
        template = EmailTemplate.query.get(template_id)
        if not template:
            raise ValueError(f'Template with ID {template_id} not found')
        
        # Check if template is assigned to any actions
        if template.actions:
            action_names = [action.name for action in template.actions]
            raise ValueError(
                f'Cannot delete template assigned to actions: {", ".join(action_names)}. '
                'Please unassign the template first.'
            )
        
        # Soft delete
        template.is_active = False
        db.session.commit()
        
        logger.info(f'Deleted email template: {template.name} (ID: {template.id})')
        return True
    
    @staticmethod
    def get_all_actions() -> List[EmailAction]:
        """
        Get all available email actions.
        
        Returns:
            List of EmailAction objects
        """
        return EmailAction.query.order_by(EmailAction.name).all()
    
    @staticmethod
    def get_action_by_key(action_key: str) -> Optional[EmailAction]:
        """
        Get email action by its key (used in code).
        
        Args:
            action_key: Action key (e.g., 'password_reset')
            
        Returns:
            EmailAction object or None
        """
        return EmailAction.query.filter_by(action_key=action_key).first()
    
    @staticmethod
    def get_action_by_id(action_id: int) -> Optional[EmailAction]:
        """
        Get email action by ID.
        
        Args:
            action_id: Action ID
            
        Returns:
            EmailAction object or None
        """
        return EmailAction.query.get(action_id)
    
    @staticmethod
    def assign_template_to_action(action_id: int, template_id: Optional[int]) -> EmailAction:
        """
        Assign (or unassign) a template to an email action.
        
        Args:
            action_id: ID of email action
            template_id: ID of template to assign, or None to unassign
            
        Returns:
            Updated EmailAction object
            
        Raises:
            ValueError: If action or template not found
        """
        action = EmailAction.query.get(action_id)
        if not action:
            raise ValueError(f'Email action with ID {action_id} not found')
        
        if template_id is not None:
            template = EmailTemplate.query.get(template_id)
            if not template:
                raise ValueError(f'Template with ID {template_id} not found')
            if not template.is_active:
                raise ValueError('Cannot assign inactive template to action')
            
            action.template_id = template_id
            logger.info(f'Assigned template "{template.name}" to action "{action.name}"')
        else:
            action.template_id = None
            logger.info(f'Unassigned template from action "{action.name}"')
        
        db.session.commit()
        return action
    
    @staticmethod
    def get_template_for_action(action_key: str) -> Optional[EmailTemplate]:
        """
        Get the template assigned to a specific action (for use in code).
        
        Args:
            action_key: Action key (e.g., 'password_reset')
            
        Returns:
            EmailTemplate object or None if action has no template
        """
        action = EmailAction.query.filter_by(action_key=action_key).first()
        if not action or not action.template:
            logger.warning(f'No template found for action: {action_key}')
            return None
        
        if not action.template.is_active:
            logger.warning(f'Template for action {action_key} is inactive')
            return None
        
        return action.template
    
    @staticmethod
    def render_template(template: EmailTemplate, variables: Dict) -> Dict[str, str]:
        """
        Render email template with provided variables.
        
        Args:
            template: EmailTemplate object
            variables: Dictionary of template variables
            
        Returns:
            Dictionary with 'subject', 'body_html', and 'body_text' keys
        """
        # Simple variable substitution using str.format()
        # Variables should be passed as key-value pairs matching template placeholders
        rendered = {
            'subject': template.subject,
            'body_html': template.body_html,
            'body_text': template.body_text
        }
        
        try:
            for key in rendered:
                if rendered[key]:
                    # Use format_map for safe variable substitution
                    rendered[key] = rendered[key].format(**variables)
        except KeyError as e:
            logger.error(f'Missing template variable: {e}')
            raise ValueError(f'Missing required template variable: {e}')
        
        return rendered
