"""
Email template service for managing email template business logic.
"""
from src.models.flask_mail.email_templates import EmailTemplate
from src.models.logs import EmailLog
from src.models.app_settings import AppSettings
from src.services.flask_mail.email_config import EMAIL_PURPOSES, get_purpose
from src.services.flask_mail.email_service import generate_email, send_email


def get_management_dashboard_data():
    """
    Get dashboard data for email management page.
    
    Returns:
        dict: stats, templates, recent_logs, mail_configured, mail_server, mail_port
    """
    # Get email statistics
    stats = {
        'sent': 0,
        'failed': 0,
        'pending': 0,
        'active_templates': 0
    }
    
    # Get stats from email logs (30 days)
    status_counts = EmailLog.count_by_status(days=30)
    stats['sent'] = status_counts.get('sent', 0)
    stats['failed'] = status_counts.get('failed', 0)
    stats['pending'] = status_counts.get('pending', 0)
    
    # Count active templates
    stats['active_templates'] = EmailTemplate.query.filter_by(is_active=True).count()
    
    # Get recent templates (limit 10)
    templates = EmailTemplate.query.order_by(
        EmailTemplate.is_active.desc(),
        EmailTemplate.updated_at.desc()
    ).limit(10).all()
    
    # Get recent email logs (limit 10) - filter to only email type logs
    recent_logs = EmailLog.get_recent_logs(limit=10, log_type=EmailLog.TYPE_EMAIL)
    
    # Get mail configuration status
    settings = AppSettings.get_settings()
    mail_configured, missing_fields = settings.test_mail_config()
    
    return {
        'stats': stats,
        'templates': templates,
        'recent_logs': recent_logs,
        'mail_configured': mail_configured,
        'mail_server': settings.mail_server,
        'mail_port': settings.mail_port
    }


def get_email_template_by_id(template_id):
    """
    Get an email template by ID.
    
    Args:
        template_id: ID of the template
        
    Returns:
        EmailTemplate or None
    """
    return EmailTemplate.query.get(template_id)


def create_email_template(purpose, name, subject_template, body_html_template, 
                          body_text_template, current_user_id):
    """
    Create a new email template.
    
    Args:
        purpose: Email purpose
        name: Template name
        subject_template: Subject template
        body_html_template: HTML body template
        body_text_template: Text body template
        current_user_id: ID of user creating the template
        
    Returns:
        EmailTemplate: The created template
        
    Raises:
        ValueError: If validation fails
    """
    # Validate required fields
    if not all([purpose, name, subject_template, body_html_template, body_text_template]):
        raise ValueError("All fields are required.")
    
    # Validate purpose exists
    if purpose not in EMAIL_PURPOSES:
        raise ValueError("Invalid email purpose selected.")
    
    # Create template
    template = EmailTemplate(
        purpose=purpose,
        name=name,
        subject_template=subject_template,
        body_html_template=body_html_template,
        body_text_template=body_text_template,
        is_active=False,  # Start as inactive
        is_default=False,
        created_by=current_user_id
    )
    
    # Validate Jinja2 syntax
    is_valid, errors = template.validate_jinja2_syntax()
    if not is_valid:
        raise ValueError(f'Template validation failed: {"; ".join(errors)}')
    
    template.save()
    return template


def update_email_template(template_id, name, subject_template, body_html_template, 
                          body_text_template):
    """
    Update an existing email template.
    
    Args:
        template_id: ID of the template to update
        name: Template name
        subject_template: Subject template
        body_html_template: HTML body template
        body_text_template: Text body template
        
    Returns:
        EmailTemplate: The updated template
        
    Raises:
        ValueError: If validation fails or template not found
    """
    template = EmailTemplate.query.get(template_id)
    if not template:
        raise ValueError("Template not found")
    
    # Validate required fields
    if not all([name, subject_template, body_html_template, body_text_template]):
        raise ValueError("All fields are required.")
    
    # Update template
    template.name = name
    template.subject_template = subject_template
    template.body_html_template = body_html_template
    template.body_text_template = body_text_template
    
    # Validate Jinja2 syntax
    is_valid, errors = template.validate_jinja2_syntax()
    if not is_valid:
        raise ValueError(f'Template validation failed: {"; ".join(errors)}')
    
    template.save()
    return template


def activate_email_template(template_id):
    """
    Activate an email template.
    
    Args:
        template_id: ID of the template to activate
        
    Returns:
        EmailTemplate: The activated template
        
    Raises:
        ValueError: If template not found or activation fails
    """
    template = EmailTemplate.query.get(template_id)
    if not template:
        raise ValueError("Template not found")
    
    template.activate()
    return template


def deactivate_email_template(template_id):
    """
    Deactivate an email template.
    
    Args:
        template_id: ID of the template to deactivate
        
    Returns:
        EmailTemplate: The deactivated template
        
    Raises:
        ValueError: If template not found
    """
    template = EmailTemplate.query.get(template_id)
    if not template:
        raise ValueError("Template not found")
    
    template.is_active = False
    template.save()
    return template


def delete_email_template(template_id):
    """
    Delete an email template.
    
    Args:
        template_id: ID of the template to delete
        
    Returns:
        str: Name of the deleted template
        
    Raises:
        ValueError: If template not found or cannot be deleted
    """
    template = EmailTemplate.query.get(template_id)
    if not template:
        raise ValueError("Template not found")
    
    # Prevent deleting default templates
    if template.is_default:
        raise ValueError("Cannot delete default templates.")
    
    # Prevent deleting active templates
    if template.is_active:
        raise ValueError("Cannot delete active templates. Deactivate it first.")
    
    template_name = template.name
    template.delete()
    return template_name


def generate_template_preview(template_id):
    """
    Generate preview data for an email template.
    
    Args:
        template_id: ID of the template
        
    Returns:
        dict: template, email_content, example_data, purpose_config
        
    Raises:
        ValueError: If template or purpose invalid
    """
    template = EmailTemplate.query.get(template_id)
    if not template:
        raise ValueError("Template not found")
    
    # Get purpose config
    purpose_config = get_purpose(template.purpose)
    
    if not purpose_config:
        raise ValueError("Invalid email purpose for this template.")
    
    # Get example data from purpose config
    example_data = purpose_config.get_example_data()
    
    # Render email content
    email_content = generate_email(template.purpose, **example_data)
    
    return {
        'template': template,
        'email_content': email_content,
        'example_data': example_data,
        'purpose_config': purpose_config
    }


def send_template_test_email(template_id, to_address, test_data):
    """
    Send a test email using the template.
    
    Args:
        template_id: ID of the template
        to_address: Recipient email address
        test_data: Dictionary of variable values for the template
        
    Returns:
        bool: True if sent successfully
        
    Raises:
        ValueError: If validation fails
    """
    if not to_address:
        raise ValueError("Recipient email address is required.")
    
    template = EmailTemplate.query.get(template_id)
    if not template:
        raise ValueError("Template not found")
    
    # Send the test email
    success = send_email(template.purpose, to_address, **test_data)
    
    if not success:
        raise ValueError(f"Failed to send test email to {to_address}. Check email logs for details.")
    
    return success
