"""
Database models initialization module
Provides SQLAlchemy database instance and base model imports
"""
from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy instance
db = SQLAlchemy()


def init_db(app):
    """
    Initialize database with Flask application
    
    Args:
        app: Flask application instance
    """
    db.init_app(app)
    
    with app.app_context():
        # Import all models here to ensure they're registered with SQLAlchemy
        from src.models.user import User
        from src.models.roles import Role, UserHasRoles
        from src.models.logbook import Logbook
        from src.models.courses_model import CourseTemplate, Course
        from src.models.student_profile import StudentProfile
        from src.models.course_enrollment import CourseEnrollment
        from src.models.email_template_model import EmailTemplate
        from src.models.email_action_model import EmailAction
        from src.models.password_reset_token import PasswordResetToken
        from src.models.payable_item_model import PayableItemTemplate, CourseTemplatePayableItem, CoursePayableItem
        from src.models.enrollment_line_items import EnrollmentLineItem
        from src.models.payment_models import Payment, PaymentAllocation, Refund
        from src.models.logs_model import Log
        
        # Create all tables if they don't exist
        db.create_all()
        
        app.logger.info("Database tables created successfully")


# Export db instance for use in models and logic layers
__all__ = ['db', 'init_db']
