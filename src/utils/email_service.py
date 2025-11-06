"""
Email sending utility with template support.
Integrates email template system with Flask-Mail.
"""
from flask_mail import Message, Mail
from src.logic.email_template_logic import EmailTemplateLogic
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """
    Service for sending templated emails.
    Integrates EmailTemplateLogic with Flask-Mail.
    """
    
    def __init__(self, mail: Mail):
        """
        Initialize email service.
        
        Args:
            mail: Flask-Mail instance
        """
        self.mail = mail
    
    def send_templated_email(
        self, 
        action_key: str, 
        recipient: str, 
        variables: dict,
        sender: str = None
    ) -> bool:
        """
        Send email using template assigned to action.
        
        Args:
            action_key: Email action key (e.g., 'password_reset')
            recipient: Recipient email address
            variables: Dictionary of template variables
            sender: Sender email (optional, uses default if not provided)
            
        Returns:
            True if email sent successfully, False otherwise
            
        Example:
            >>> email_service = EmailService(mail)
            >>> email_service.send_templated_email(
            ...     action_key='password_reset',
            ...     recipient='user@example.com',
            ...     variables={
            ...         'user_name': 'John Doe',
            ...         'reset_link': 'https://example.com/reset/abc123',
            ...         'expiry_time': '1 hour',
            ...         'app_name': 'CWMT'
            ...     }
            ... )
        """
        try:
            # Get template for action
            template = EmailTemplateLogic.get_template_for_action(action_key)
            
            if not template:
                logger.warning(
                    f"No template assigned to action '{action_key}'. "
                    f"Email to {recipient} not sent."
                )
                return False
            
            # Render template with variables
            try:
                rendered = EmailTemplateLogic.render_template(template, variables)
            except ValueError as e:
                logger.error(
                    f"Failed to render template for action '{action_key}': {e}"
                )
                return False
            
            # Create and send message
            msg = Message(
                subject=rendered['subject'],
                recipients=[recipient],
                body=rendered['body_text'],
                html=rendered['body_html'] if rendered['body_html'] else None,
                sender=sender
            )
            
            self.mail.send(msg)
            
            logger.info(
                f"Sent email '{action_key}' to {recipient} "
                f"using template '{template.name}'"
            )
            return True
            
        except Exception as e:
            logger.error(
                f"Failed to send email '{action_key}' to {recipient}: {e}"
            )
            return False
    
    def send_password_reset_email(
        self, 
        user_email: str,
        user_name: str,
        reset_link: str,
        expiry_time: str = "1 hour"
    ) -> bool:
        """
        Send password reset email.
        
        Args:
            user_email: User's email address
            user_name: User's full name
            reset_link: Password reset URL
            expiry_time: How long the link is valid
            
        Returns:
            True if sent successfully
        """
        return self.send_templated_email(
            action_key='password_reset',
            recipient=user_email,
            variables={
                'user_name': user_name,
                'user_email': user_email,
                'reset_link': reset_link,
                'expiry_time': expiry_time,
                'app_name': 'CWMT'
            }
        )
    
    def send_welcome_email(
        self,
        user_email: str,
        user_name: str,
        login_link: str
    ) -> bool:
        """
        Send welcome email to new user.
        
        Args:
            user_email: User's email address
            user_name: User's full name
            login_link: Login page URL
            
        Returns:
            True if sent successfully
        """
        return self.send_templated_email(
            action_key='welcome_email',
            recipient=user_email,
            variables={
                'user_name': user_name,
                'user_email': user_email,
                'login_link': login_link,
                'app_name': 'CWMT'
            }
        )
    
    def send_course_enrollment_email(
        self,
        user_email: str,
        user_name: str,
        course_name: str,
        course_start_date: str,
        instructor_name: str
    ) -> bool:
        """
        Send course enrollment confirmation email.
        
        Args:
            user_email: Student's email
            user_name: Student's name
            course_name: Name of the course
            course_start_date: Course start date
            instructor_name: Instructor's name
            
        Returns:
            True if sent successfully
        """
        return self.send_templated_email(
            action_key='course_enrollment',
            recipient=user_email,
            variables={
                'user_name': user_name,
                'user_email': user_email,
                'course_name': course_name,
                'course_start_date': course_start_date,
                'instructor_name': instructor_name,
                'app_name': 'CWMT'
            }
        )


# Example usage in your application:
"""
from flask import Flask
from flask_mail import Mail
from src.utils.email_service import EmailService

app = Flask(__name__)
mail = Mail(app)
email_service = EmailService(mail)

# Send password reset email
email_service.send_password_reset_email(
    user_email='user@example.com',
    user_name='John Doe',
    reset_link='https://example.com/reset/token123',
    expiry_time='1 hour'
)

# Or send any templated email
email_service.send_templated_email(
    action_key='custom_action',
    recipient='user@example.com',
    variables={'key': 'value'}
)
"""
