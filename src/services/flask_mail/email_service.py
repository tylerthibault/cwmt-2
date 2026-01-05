

def generate_email(purpose, **kwargs):
    """Generate email content based on purpose and context variables.
    
    Args:
        purpose: The email purpose code (e.g., 'new_user', 'password_reset')
        **kwargs: Variable context values to render in the template
                  (e.g., user_name='John', user_email='john@example.com')
    
    Returns:
        dict with 'subject', 'html_body', 'text_body'
    
    Example:
        generate_email('new_user', 
                      user_name='John Smith',
                      user_email='john@example.com',
                      temp_password='Pass123!')
    """
    from src.services.flask_mail.email_config import get_purpose
    from src.models.flask_mail.email_templates import EmailTemplate

    # Get and validate the email purpose
    try:
        email_purpose = get_purpose(purpose)
    except ValueError as e:
        raise ValueError(f"Unknown email purpose: {purpose}") from e

    # Get the active template for this purpose
    email_template = EmailTemplate.get_active_template(purpose)
    if not email_template:
        raise ValueError(f"No active email template found for purpose: {purpose}")

    # Validate that all required variables are provided
    email_purpose.validate_context(kwargs)

    # Render the template with the provided variables
    return email_template.render_all(kwargs)


def send_email(purpose, to_address, **kwargs):
    """Send an email using a template. This is the main entry point for sending emails.
    
    Args:
        purpose: The email purpose code (e.g., 'new_user', 'password_reset')
        to_address: Recipient email address
        **kwargs: Variable context values to render in the template
    
    Returns:
        bool: True if email sent successfully, False otherwise
    
    Example:
        send_email('new_user', 
                   'john@example.com',
                   user_name='John Smith',
                   user_email='john@example.com',
                   temp_password='Pass123!',
                   login_link='https://cwmt.example.com/login',
                   support_email='support@cwmt.example.com')
    """
    from flask_mail import Message, Mail
    from flask import current_app
    from src.models.flask_mail.email_logs import EmailLog
    from src.models.flask_mail.email_templates import EmailTemplate
    
    email_log = None
    
    try:
        # Generate email content from template
        email_content = generate_email(purpose, **kwargs)
        
        # Get the template for logging
        template = EmailTemplate.get_active_template(purpose)
        
        # Create email log entry (pending status)
        email_log = EmailLog.create_log(
            purpose=purpose,
            recipient_email=to_address,
            template_id=template.id if template else None,
            subject=email_content['subject'],
            body_html=email_content['html_body'],
            body_text=email_content['text_body']
        )
        
        # Get Flask-Mail instance
        mail = current_app.extensions.get('mail')
        if not mail:
            raise RuntimeError("Flask-Mail is not initialized")
        
        # Create and send message
        msg = Message(
            subject=email_content['subject'],
            recipients=[to_address],
            html=email_content['html_body'],
            body=email_content['text_body'],
            sender=current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@cwmt.example.com')
        )
        
        mail.send(msg)
        
        # Mark as sent
        if email_log:
            email_log.mark_sent()
        
        return True
        
    except Exception as e:
        # Mark as failed with error message
        if email_log:
            email_log.mark_failed(str(e))
        
        # Re-raise for controller to handle
        raise RuntimeError(f"Failed to send email: {str(e)}") from e
