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
        
        # Create all tables if they don't exist
        db.create_all()
        
        app.looger.info("Database tables created successfully")
        
        # Seed default roles on first database creation
        from seeds.seed_roles import seed_default_roles
        seed_default_roles(app)
        
        # Seed default users with test accounts
        from seeds.seed_users import seed_default_users
        seed_default_users(app)
        
        # Seed default course templates
        from seeds.seed_courses import seed_default_course_templates
        seed_default_course_templates(app)


# Export db instance for use in models and logic layers
__all__ = ['db', 'init_db']
