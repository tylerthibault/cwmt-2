

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

    # Auto-generate user_name from first_name and last_name if not provided
    if 'user_name' not in kwargs and ('first_name' in kwargs or 'last_name' in kwargs):
        first_name = kwargs.get('first_name', '').strip()
        last_name = kwargs.get('last_name', '').strip()
        kwargs['user_name'] = f"{first_name} {last_name}".strip() or 'User'

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
    from src.models.logs import EmailLog
    from src.models.flask_mail.email_templates import EmailTemplate
    
    # Helper function to clean email content
    def clean_for_email(text):
        """Clean text for email compatibility by replacing problematic Unicode characters."""
        
        if not text:
            return ''
        # Replace non-breaking space (\xa0) with regular space
        text = text.replace('\xa0', ' ')
        # Replace other common problematic Unicode characters
        text = text.replace('\u2018', "'").replace('\u2019', "'")  # Smart quotes
        text = text.replace('\u201c', '"').replace('\u201d', '"')  # Smart double quotes
        text = text.replace('\u2013', '-').replace('\u2014', '-')  # En/em dashes
        return text
    
    email_log = None
    
    try:
        # Generate email content from template
        email_content = generate_email(purpose, **kwargs)
        
        # DEBUG: Check for problematic characters in raw content
        print("\n" + "="*80)
        print("DEBUG: Email Content Before Cleaning")
        print("="*80)
        print(f"Subject: {repr(email_content['subject'])}")
        print(f"Subject contains \\xa0: {'\\xa0' in email_content['subject']}")
        print(f"HTML contains \\xa0: {'\\xa0' in email_content['html_body']}")
        print(f"Text contains \\xa0: {'\\xa0' in email_content['text_body']}")
        
        # Clean all content BEFORE using it anywhere to avoid encoding errors
        cleaned_subject = clean_for_email(email_content['subject'])
        cleaned_html = clean_for_email(email_content['html_body'])
        cleaned_text = clean_for_email(email_content['text_body'])
        
        # DEBUG: Verify cleaning worked
        print("\nDEBUG: After Cleaning")
        print(f"Cleaned subject: {repr(cleaned_subject)}")
        print(f"Cleaned subject contains \\xa0: {'\\xa0' in cleaned_subject}")
        print(f"Cleaned HTML contains \\xa0: {'\\xa0' in cleaned_html}")
        print(f"Cleaned text contains \\xa0: {'\\xa0' in cleaned_text}")
        
        # Get the template for logging
        template = EmailTemplate.get_active_template(purpose)
        
        # DEBUG: Check recipient and sender
        print(f"\nDEBUG: Email Addresses")
        print(f"To: {repr(to_address)}")
        sender_raw = current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@cwmt.example.com')
        print(f"Sender (raw): {repr(sender_raw)}")
        print(f"Sender contains \\xa0: {'\\xa0' in str(sender_raw)}")
        
        # Create email log entry (pending status) with cleaned content
        print("\nDEBUG: Creating email log...")
        email_log = EmailLog.create_log(
            purpose=purpose,
            recipient_email=to_address,
            template_id=template.id if template else None,
            subject=cleaned_subject,
            body_html=cleaned_html,
            body_text=cleaned_text
        )
        print("DEBUG: Email log created successfully")
        
        # Get Flask-Mail instance
        mail = current_app.extensions.get('mail')
        if not mail:
            raise RuntimeError("Flask-Mail is not initialized")
        
        # Get and clean sender address
        sender = current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@cwmt.example.com')
        cleaned_sender = clean_for_email(sender)
        print(f"Sender (cleaned): {repr(cleaned_sender)}")
        
        # Create message with cleaned content
        print("\nDEBUG: Creating Flask-Mail Message object...")
        msg = Message(
            subject=cleaned_subject,
            recipients=[to_address],
            sender=cleaned_sender
        )
        
        # Manually set body parts with explicit charset to avoid ASCII encoding errors
        msg.body = cleaned_text
        msg.html = cleaned_html
        msg.charset = 'utf-8'
        
        print("DEBUG: Message object created successfully")
        print(f"DEBUG: Message charset set to: {msg.charset}")
        
        print("\nDEBUG: Sending email via mail.send()...")
        mail.send(msg)
        print("DEBUG: Email sent successfully!")
        print("="*80 + "\n")
        
        # Mark as sent
        print("DEBUG: Marking email log as sent...")
        if email_log:
            email_log.mark_sent()
        print("DEBUG: Email log marked as sent")
        
        print("DEBUG: Returning True - email send complete!")
        return True
        
    except Exception as e:
        print(f"\n!!! DEBUG: EXCEPTION CAUGHT !!!")
        print(f"Exception type: {type(e).__name__}")
        print(f"Exception message: {str(e)}")
        print(f"Exception repr: {repr(e)}")
        import traceback
        print(f"Full traceback:")
        traceback.print_exc()
        print("="*80 + "\n")
        
        # Mark as failed with error message
        if email_log:
            email_log.mark_failed(str(e))
        
        # Re-raise for controller to handle
        raise RuntimeError(f"Failed to send email: {str(e)}") from e
