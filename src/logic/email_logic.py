"""
Email Logic Module

Handles all email sending operations using email templates and actions.
This module is responsible for:
- Retrieving the correct template for an action
- Rendering templates with provided variables
- Sending emails via Flask-Mail
- Logging email sending attempts

All business logic for email operations should be in this module.
"""
from flask import current_app
from flask_mail import Message
from src import mail
from src.models.email_action_model import EmailAction
from src.models.email_template_model import EmailTemplate
from src.logic.setting_logic import SettingsLogic


class EmailLogic:
    """Business logic for email operations"""
    
    @staticmethod
    def send_email(action_key, recipient_email, variables=None, **kwargs):
        """
        Send an email using the template assigned to the specified action.
        
        Args:
            action_key (str): The key identifying the email action (e.g., 'password_reset')
            recipient_email (str): Email address of the recipient
            variables (dict): Dictionary of variables to substitute in the template
            **kwargs: Additional email parameters (cc, bcc, reply_to, attachments)
        
        Returns:
            bool: True if email was sent successfully, False otherwise
        
        Raises:
            ValueError: If action_key is invalid or no template is assigned
            Exception: If email sending fails
        
        Example:
            EmailLogic.send_email(
                'password_reset',
                'user@example.com',
                variables={
                    'user_name': 'John Doe',
                    'reset_link': 'https://example.com/reset/abc123',
                    'expiry_time': '24 hours'
                }
            )
        """
        if variables is None:
            variables = {}
        
        try:
            # Get the email action
            action = EmailAction.query.filter_by(action_key=action_key).first()
            if not action:
                raise ValueError(f"Email action '{action_key}' not found")
            
            # Check if a template is assigned to this action
            if not action.template_id:
                raise ValueError(f"No template assigned to action '{action_key}'")
            
            # Get the template
            template = EmailTemplate.query.get(action.template_id)
            if not template:
                raise ValueError(f"Template not found for action '{action_key}'")
            
            # Check if template is active
            if not template.is_active:
                raise ValueError(f"Template for action '{action_key}' is not active")
            
            # Add default variables
            default_variables = EmailLogic._get_default_variables()
            merged_variables = {**default_variables, **variables}
            
            # Render the template
            rendered_subject = EmailLogic._render_template_string(template.subject, merged_variables)
            rendered_body_html = EmailLogic._render_template_string(template.body_html, merged_variables)
            rendered_body_text = EmailLogic._render_template_string(template.body_text, merged_variables)
            
            # Get email configuration
            mail_config = SettingsLogic.get_flask_mail_config()
            default_sender = mail_config.get('MAIL_DEFAULT_SENDER')
            
            if not default_sender:
                raise ValueError("MAIL_DEFAULT_SENDER is not configured in email settings")
            
            # Update app config and reinitialize mail
            current_app.config.update(mail_config)
            mail.init_app(current_app)
            
            # Create the email message
            msg = Message(
                subject=rendered_subject,
                recipients=[recipient_email],
                body=rendered_body_text,
                html=rendered_body_html,
                sender=default_sender
            )
            
            # Add optional parameters
            if 'cc' in kwargs:
                msg.cc = kwargs['cc'] if isinstance(kwargs['cc'], list) else [kwargs['cc']]
            if 'bcc' in kwargs:
                msg.bcc = kwargs['bcc'] if isinstance(kwargs['bcc'], list) else [kwargs['bcc']]
            if 'reply_to' in kwargs:
                msg.reply_to = kwargs['reply_to']
            if 'attachments' in kwargs:
                for attachment in kwargs['attachments']:
                    msg.attach(**attachment)
            
            # Log the attempt
            current_app.logger.info(f"Sending email: action='{action_key}', recipient='{recipient_email}', template='{template.name}'")
            
            # Send the email
            mail.send(msg)
            
            # Log success
            current_app.logger.info(f"Email sent successfully: action='{action_key}', recipient='{recipient_email}'")
            
            return True
            
        except ValueError as e:
            # Log validation errors
            current_app.logger.error(f"Email validation error: {str(e)}")
            raise
            
        except Exception as e:
            # Log sending errors
            current_app.logger.error(f"Failed to send email: action='{action_key}', recipient='{recipient_email}', error={str(e)}")
            raise
    
    @staticmethod
    def send_test_email(recipient_email, test_message="This is a test email"):
        """
        Send a test email to verify email configuration.
        
        Args:
            recipient_email (str): Email address to send test to
            test_message (str): Custom test message
        
        Returns:
            bool: True if email was sent successfully
        """
        try:
            return EmailLogic.send_email(
                'test_email',
                recipient_email,
                variables={
                    'user_name': 'Test User',
                    'test_message': test_message
                }
            )
        except ValueError as e:
            # If test_email action doesn't have a template, raise helpful error
            if "No template assigned" in str(e):
                raise ValueError(
                    "Please assign a template to the 'Test Email' action before sending test emails. "
                    "Go to Email Templates → Email Actions → Assign Template."
                )
            raise
    
    @staticmethod
    def send_password_reset_email(user_email, user_name, reset_link, expiry_time="24 hours"):
        """
        Send a password reset email.
        
        Args:
            user_email (str): User's email address
            user_name (str): User's full name
            reset_link (str): Unique password reset link
            expiry_time (str): How long the link is valid
        
        Returns:
            bool: True if email was sent successfully
        """
        return EmailLogic.send_email(
            'password_reset',
            user_email,
            variables={
                'user_name': user_name,
                'reset_link': reset_link,
                'expiry_time': expiry_time
            }
        )
    
    @staticmethod
    def send_new_student_email(user_email, user_name, student_id, login_link):
        """
        Send welcome email to new student.
        
        Args:
            user_email (str): Student's email address
            user_name (str): Student's full name
            student_id (str): Student ID number
            login_link (str): Link to login page
        
        Returns:
            bool: True if email was sent successfully
        """
        return EmailLogic.send_email(
            'new_student',
            user_email,
            variables={
                'user_name': user_name,
                'user_email': user_email,
                'student_id': student_id,
                'login_link': login_link
            }
        )
    
    @staticmethod
    def send_new_instructor_email(user_email, user_name, login_link, instructor_resources_link):
        """
        Send welcome email to new instructor.
        
        Args:
            user_email (str): Instructor's email address
            user_name (str): Instructor's full name
            login_link (str): Link to login page
            instructor_resources_link (str): Link to instructor resources
        
        Returns:
            bool: True if email was sent successfully
        """
        return EmailLogic.send_email(
            'new_instructor',
            user_email,
            variables={
                'user_name': user_name,
                'user_email': user_email,
                'login_link': login_link,
                'instructor_resources_link': instructor_resources_link
            }
        )
    
    @staticmethod
    def send_student_course_reminder(user_email, user_name, course_name, course_date, 
                                     course_time, course_location, instructor_name, days_until):
        """
        Send course reminder to student.
        
        Args:
            user_email (str): Student's email address
            user_name (str): Student's full name
            course_name (str): Name of the course
            course_date (str): Date of the course
            course_time (str): Time of the course
            course_location (str): Location of the course
            instructor_name (str): Name of the instructor
            days_until (int): Number of days until the course
        
        Returns:
            bool: True if email was sent successfully
        """
        return EmailLogic.send_email(
            'student_course_reminder',
            user_email,
            variables={
                'user_name': user_name,
                'course_name': course_name,
                'course_date': course_date,
                'course_time': course_time,
                'course_location': course_location,
                'instructor_name': instructor_name,
                'days_until': days_until
            }
        )
    
    @staticmethod
    def send_instructor_course_reminder(user_email, user_name, course_name, course_date,
                                        course_time, course_location, student_count, 
                                        enrolled_students, days_until):
        """
        Send course reminder to instructor.
        
        Args:
            user_email (str): Instructor's email address
            user_name (str): Instructor's full name
            course_name (str): Name of the course
            course_date (str): Date of the course
            course_time (str): Time of the course
            course_location (str): Location of the course
            student_count (int): Number of enrolled students
            enrolled_students (str): Formatted list of student names
            days_until (int): Number of days until the course
        
        Returns:
            bool: True if email was sent successfully
        """
        return EmailLogic.send_email(
            'instructor_course_reminder',
            user_email,
            variables={
                'user_name': user_name,
                'course_name': course_name,
                'course_date': course_date,
                'course_time': course_time,
                'course_location': course_location,
                'student_count': student_count,
                'enrolled_students': enrolled_students,
                'days_until': days_until
            }
        )
    
    @staticmethod
    def _render_template_string(template_string, variables):
        """
        Render a template string with variables using Python's string.format().
        
        Args:
            template_string (str): Template string with {variable} placeholders
            variables (dict): Dictionary of variables to substitute
        
        Returns:
            str: Rendered string with variables substituted
        """
        try:
            return template_string.format(**variables)
        except KeyError as e:
            # If a required variable is missing, log it but don't fail
            current_app.logger.warning(f"Missing template variable: {str(e)}")
            # Return the original string with missing variables still in brackets
            return template_string
        except Exception as e:
            current_app.logger.error(f"Error rendering template: {str(e)}")
            return template_string
    
    @staticmethod
    def _get_default_variables():
        """
        Get default variables that are available to all email templates.
        
        Returns:
            dict: Dictionary of default variables
        """
        # Get app name from settings or use default
        app_name = SettingsLogic.get_setting('app_name') or 'CWMT'
        
        return {
            'app_name': app_name,
            'year': '2025'  # Could be dynamic: datetime.now().year
        }
    
    @staticmethod
    def preview_email(action_key, variables=None):
        """
        Preview an email without sending it.
        
        Args:
            action_key (str): The key identifying the email action
            variables (dict): Dictionary of variables to substitute in the template
        
        Returns:
            dict: Dictionary with 'subject', 'body_html', and 'body_text'
        
        Raises:
            ValueError: If action_key is invalid or no template is assigned
        """
        if variables is None:
            variables = {}
        
        # Get the email action
        action = EmailAction.query.filter_by(action_key=action_key).first()
        if not action:
            raise ValueError(f"Email action '{action_key}' not found")
        
        # Check if a template is assigned to this action
        if not action.template_id:
            raise ValueError(f"No template assigned to action '{action_key}'")
        
        # Get the template
        template = EmailTemplate.query.get(action.template_id)
        if not template:
            raise ValueError(f"Template not found for action '{action_key}'")
        
        # Add default variables
        default_variables = EmailLogic._get_default_variables()
        merged_variables = {**default_variables, **variables}
        
        # Render the template
        return {
            'subject': EmailLogic._render_template_string(template.subject, merged_variables),
            'body_html': EmailLogic._render_template_string(template.body_html, merged_variables),
            'body_text': EmailLogic._render_template_string(template.body_text, merged_variables)
        }
