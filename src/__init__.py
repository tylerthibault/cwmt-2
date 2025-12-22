from flask import Flask
from .models.main import db

def create_app():
    app = Flask(__name__)
    app.secret_key = 'your_secret_key'  # Replace with a secure key in production

    # Register blueprints
    init_blueprints(app)
    
    # Initialize database
    init_db(app)

    return app

def init_db(app):
    """Initialize the sqlalchemy database connection and create all tables."""
    
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cwmt.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['BCRYPT_LOG_ROUNDS'] = 12
    # Initialize db with app
    db.init_app(app)

    from src.models.user_folder.users import User
    from src.models.user_folder.students import Student
    from src.models.user_folder.instructors import Instructor
    from src.models.user_folder.admins import Admin
    from src.models.user_folder.superusers import Superuser
    
    # Create all tables
    with app.app_context():
        db.create_all()
    
    return db

def init_blueprints(app):
    """Register all blueprints with the Flask app."""
    
    from src.controllers.routes import main_bp
    app.register_blueprint(main_bp)

    from src.controllers.users.auth import auth_bp
    app.register_blueprint(auth_bp)

    from src.controllers.users.student import student_bp
    app.register_blueprint(student_bp)

    from src.controllers.users.instructor import instructor_bp
    app.register_blueprint(instructor_bp)

    from src.controllers.users.admin import admin_bp
    app.register_blueprint(admin_bp)

    from src.controllers.users.superuser import superuser_bp
    app.register_blueprint(superuser_bp)

    from src.controllers.seeding import seed_bp
    app.register_blueprint(seed_bp)
    
    return app


