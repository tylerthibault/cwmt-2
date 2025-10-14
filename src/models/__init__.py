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
        
        # Create all tables if they don't exist
        db.create_all()
        
        app.looger.info("Database tables created successfully")
        
        # Seed default roles on first database creation
        from src.utils.seed_roles import seed_default_roles
        seed_default_roles(app)


# Export db instance for use in models and logic layers
__all__ = ['db', 'init_db']
