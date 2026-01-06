from flask import Flask
from flask_mail import Mail
from flask_migrate import Migrate
from .models.main import db

mail = Mail()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.secret_key = '5d67dfa6d956b2a6970680d9'  # Replace with a secure key in production

    # Load configuration
    init_config(app)
    
    # Register blueprints
    init_blueprints(app)
    
    # Initialize database
    init_db(app) 
    
    # Initialize Flask-Mail
    mail.init_app(app)
    
    # Initialize Flask-Migrate
    migrate.init_app(app, db)

    return app

def init_config(app):
    """Load configuration from environment variables."""
    import os
    
    # Mail configuration
    app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    app.config['MAIL_USE_SSL'] = os.environ.get('MAIL_USE_SSL', 'False').lower() == 'true'
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', 
                                                        os.environ.get('MAIL_USERNAME', 'noreply@cwmt.com'))

def init_db(app):
    """Initialize the sqlalchemy database connection and create all tables."""
    import os
    
    # Use DATABASE_URL from environment if available, otherwise fall back to SQLite
    database_url = os.environ.get('DATABASE_URL')
    
    if database_url:
        # Use the DATABASE_URL from environment (for production/CapRover)
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        # Fall back to SQLite for local development
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
    from src.models.course_folder.course_templates import CourseTemplate
    from src.models.course_folder.course_instances import CourseInstance
    from src.models.course_folder.payable_templates import PayableTemplate
    from src.models.course_folder.enrollments import Enrollment
    from src.models.announcements import Announcement
    from src.models.doorman import Doorman
    from src.models.logs import Log

    # stripe models
    from src.models.stripe.payments import Payment
    from src.models.stripe.payment_line_items import PaymentLineItem
    from src.models.stripe.stripe_webhook_events import StripeWebhookEvent 
    
    # flask-mail models
    from src.models.flask_mail.email_templates import EmailTemplate
    from src.models.app_settings import AppSettings

    
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

    from src.controllers.courses.course_template import course_temp_bp
    app.register_blueprint(course_temp_bp)

    from src.controllers.courses.course_instances import courses_bp
    app.register_blueprint(courses_bp)

    from src.controllers.courses.payable_template import payable_temp_bp
    app.register_blueprint(payable_temp_bp)

    from src.controllers.announcements import announcements_bp
    app.register_blueprint(announcements_bp)
    
    # Stripe payments
    from src.controllers.payments.stripe_payments import stripe_payments_bp
    app.register_blueprint(stripe_payments_bp)
    
    from src.controllers.payments.stripe_webhooks import stripe_webhooks_bp
    app.register_blueprint(stripe_webhooks_bp)

    # Flask Mail
    from src.controllers.flask_mail.mail_routes import mail_bp
    app.register_blueprint(mail_bp)
    
    # DEV
    from src.controllers.seeding import seed_bp
    app.register_blueprint(seed_bp)
    
    from src.dev.database import database_bp
    app.register_blueprint(database_bp)
    
    return app


