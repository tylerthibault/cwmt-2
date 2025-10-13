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
        # Add more model imports as they are created
        # from src.models.course import Course
        # from src.models.enrollment import Enrollment
        
        # Create all tables if they don't exist
        db.create_all()
        
        app.looger.info("Database tables created successfully")


# Export db instance for use in models and logic layers
__all__ = ['db', 'init_db']
