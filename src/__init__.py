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
    
    # Initialize Flask-Mail with database settings
    init_mail(app)
    
    # Initialize Flask-Migrate
    migrate.init_app(app, db)

    return app

def init_config(app):
    """Load configuration from environment variables."""
    import os
    
    # Basic mail configuration - can be overridden by database settings
    # These serve as fallbacks if database settings aren't configured yet
    app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    app.config['MAIL_USE_SSL'] = os.environ.get('MAIL_USE_SSL', 'False').lower() == 'true'
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', 
                                                        os.environ.get('MAIL_USERNAME', 'noreply@cwmt.com'))

def init_mail(app):
    """Initialize Flask-Mail with database settings if available."""
    mail.init_app(app)
    
    # Try to load email config from database
    try:
        with app.app_context():
            from src.models.app_settings import AppSettings
            settings = AppSettings.get_settings()
            
            # Check if database settings are complete
            is_valid, missing_fields = settings.test_mail_config()
            
            if is_valid:
                # Update app config with database settings
                mail_config = settings.get_mail_config()
                for key, value in mail_config.items():
                    if value is not None:  # Only override if value exists
                        app.config[key] = value
                
                # Reinitialize mail with updated config
                mail.init_app(app)
                print("✓ Email configuration loaded from database")
            else:
                print(f"⚠ Email settings incomplete in database (missing: {', '.join(missing_fields)})")
                print("Using environment variable configuration for email.")
    except Exception as e:
        # If database settings aren't available, continue with environment variables
        print(f"Warning: Could not load email settings from database: {e}")
        print("Using environment variable configuration for email.")

def reload_mail_config(app):
    """Reload mail configuration from database without server restart."""
    try:
        from src.models.app_settings import AppSettings
        settings = AppSettings.get_settings()
        
        # Check if database settings are complete
        is_valid, missing_fields = settings.test_mail_config()
        
        if is_valid:
            # Update app config with database settings
            mail_config = settings.get_mail_config()
            for key, value in mail_config.items():
                if value is not None:
                    app.config[key] = value
            
            # Reinitialize mail with updated config
            mail.init_app(app)
            return True, "Email configuration reloaded successfully"
        else:
            return False, f"Email settings incomplete (missing: {', '.join(missing_fields)})"
    except Exception as e:
        return False, f"Failed to reload email config: {str(e)}"

def init_db(app):
    """Initialize the sqlalchemy database connection and create all tables."""
    import os

    # Use DATABASE_URL from environment if available, otherwise fall back to SQLite
    # database_url = os.environ.get('DATABASE_URL')
    database_url = 'sqlite:///cwmt.db'
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
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

    # stripe models
    from src.models.stripe.payments import Payment
    from src.models.stripe.payment_line_items import PaymentLineItem
    from src.models.stripe.stripe_webhook_events import StripeWebhookEvent 
    
    # flask-mail models
    from src.models.flask_mail.email_templates import EmailTemplate
    from src.models.logs import Log
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
    
    # Payment management
    from src.controllers.payments.payment_management import payments_bp
    app.register_blueprint(payments_bp)
    
    # Enrollment management
    from src.controllers.enrollment_management import enrollments_bp
    app.register_blueprint(enrollments_bp)
    
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


