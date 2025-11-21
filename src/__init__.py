from flask import Flask
from src.utils.looger import Logger, LogLevel
from config import config
from flask_bcrypt import Bcrypt 
from src.logic.setting_logic import SettingsLogic
from flask_mail import Mail

# Initialize Flask-Mail
mail = Mail()

def create_app(config_name='development'):
    """Application factory pattern for creating Flask app instances"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize logger
    init_logger(app)
    app.looger.info("------------------- Application starting up -------------------")
    
    # Initialize Bcrypt
    app.bcrypt = Bcrypt(app)
    
    # Initialize Flask-Mail
    mail.init_app(app)
    
    # Initialize database
    init_database(app)

    with app.app_context():
        # Initialize default settings
        SettingsLogic.initialize_default_mail_settings()
        
        # Load email config from database
        mail_config = SettingsLogic.get_flask_mail_config()
        app.config.update(mail_config)
    
    # Initialize blueprints
    init_blueprints(app)
    
    app.looger.info("Flask application created successfully", 
                   config=config_name,
                   debug=app.config['DEBUG'])
    
    return app


# def init_database(app):
#     """Initialize database connections and create tables"""
#     app.looger.info("Database initialization started")
    
#     try:
#         from src.models import init_db
#         init_db(app)
        
#         db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', 'Not configured')
#         app.looger.info("Database initialized successfully", database_uri=db_uri)
        
#     except ImportError as e:
#         app.looger.error("Failed to import database module", error=str(e))
#         raise
#     except Exception as e:
#         app.looger.error("Database initialization failed", error=str(e))
#         raise
    
#     app.looger.info("Database initialization completed")

from flask import Flask
from src.utils.looger import Logger, LogLevel
from config import config
from flask_bcrypt import Bcrypt 
from src.logic.setting_logic import SettingsLogic
from flask_mail import Mail

# Initialize Flask-Mail
mail = Mail()

def create_app(config_name='development'):
    """Application factory pattern for creating Flask app instances"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize logger
    init_logger(app)
    app.looger.info("------------------- Application starting up -------------------")
    
    # Initialize Bcrypt
    app.bcrypt = Bcrypt(app)
    
    # Initialize Flask-Mail
    mail.init_app(app)
    
    # Initialize database
    init_database(app)

    with app.app_context():
        # Initialize default settings
        SettingsLogic.initialize_default_mail_settings()
        
        # Load email config from database
        mail_config = SettingsLogic.get_flask_mail_config()
        app.config.update(mail_config)
        
        # Auto-seed database if enabled (typically in development)
        if app.config.get('AUTO_SEED', False):
            run_auto_seed(app)
    
    # Initialize blueprints
    init_blueprints(app)
    
    app.looger.info(f"Flask application created successfully - config={config_name}, debug={app.config['DEBUG']}")
    
    return app


def run_auto_seed(app):
    """Run database seeding if not already seeded"""
    import os
    from pathlib import Path
    
    # Check if database has been seeded using a flag file
    instance_path = Path(app.instance_path)
    seed_flag_file = instance_path / '.seeded'
    
    if seed_flag_file.exists():
        app.looger.info("Database already seeded, skipping auto-seed")
        return
    
    app.looger.info("AUTO_SEED enabled - Running database seeds...")
    
    try:
        # Import seed functions
        from seeds.seed_roles import seed_default_roles
        from seeds.seed_users import seed_default_users
        from seeds.seed_courses import seed_all_courses
        from seeds.seed_students import seed_all_students
        from seeds.seed_email_settings import seed_email_settings
        from seeds.seed_email_actions import seed_email_actions
        from seeds.seed_email_templates import seed_email_templates
        
        # Run seeds in order
        seed_default_roles(app)
        seed_default_users(app)
        seed_all_courses(app)
        seed_all_students(app)
        seed_email_settings(app)
        seed_email_actions(app)
        seed_email_templates(app)
        
        # Create flag file to mark database as seeded
        seed_flag_file.write_text('seeded')
        app.looger.info("✓ Auto-seed completed successfully")
        
    except Exception as e:
        app.looger.error(f"Auto-seed failed: {e}")
        # Don't raise - allow app to continue even if seeding fails


def init_logger(app):
    """Initialize and attach the custom logger to the Flask app"""
    # Determine log level based on configuration
    logger = Logger(
        name="CWMT",
        log_file=app.config.get('LOG_FILE'),
        level="DEBUG"
    )
    app.looger = logger


def init_blueprints(app):
    """Register all application blueprints"""
    app.looger.info("Blueprints initialization started")
    
    try:
        # Register main routes blueprint
        from src.controllers.routes import main_bp
        app.register_blueprint(main_bp)
        
        from src.controllers.auth_controller import auth_bp
        app.register_blueprint(auth_bp)
                
        from src.controllers.user_controller import user_bp
        app.register_blueprint(user_bp)

        from src.controllers.super_user_controller import super_user_bp
        app.register_blueprint(super_user_bp)

        from src.controllers.user_admin_controller import user_admin_bp
        app.register_blueprint(user_admin_bp)

        from src.controllers.instructor_controller import instructor_bp
        app.register_blueprint(instructor_bp)

        from src.controllers.student_controller import student_bp
        app.register_blueprint(student_bp)

    except ImportError as e:
        app.looger.warning(f"Failed to import routes: {e}")
    except Exception as e:
        app.looger.error(f"Blueprint registration failed: {e}")
    
    app.looger.info("Blueprints initialization completed")


def init_database(app):
    """Initialize database connections and create tables"""
    import os
    from sqlalchemy.engine import make_url

    app.looger.info("Database initialization started")

    # Resolve and ensure sqlite DB path exists if using sqlite
    uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
    app.looger.info(f"Configured SQLALCHEMY_DATABASE_URI: {uri}")

    if uri and uri.startswith('sqlite'):
        try:
            u = make_url(uri)
            db_path = u.database  # may be relative like 'instance/cwmt.db'
        except Exception:
            # fallback extraction
            db_path = uri.replace('sqlite:///', '', 1)

        # If the path is relative, resolve it to a deterministic absolute path.
        if not os.path.isabs(db_path):
            # If the DB path starts with 'instance/', resolve against Flask's instance_path.
            if db_path.startswith('instance/') or db_path.startswith('instance\\'):
                rel = db_path.split('/', 1)[-1] if '/' in db_path else db_path.split('\\', 1)[-1]
                db_path = os.path.join(app.instance_path, rel)
            else:
                # otherwise resolve against app root
                db_path = os.path.join(app.root_path, db_path)

        db_path = os.path.abspath(db_path)
        app.looger.info(f"Resolved DB absolute path: {db_path}")

        # Ensure parent directory exists before SQLAlchemy tries to open/create the DB file
        parent = os.path.dirname(db_path) or app.instance_path
        try:
            os.makedirs(parent, exist_ok=True)
            app.looger.info(f"Ensured parent directory exists: {parent}")
        except Exception as e:
            app.looger.error(f"Failed to create DB parent directory: {e}")
            raise

        # Normalize to forward slashes for the sqlite URI (especially on Windows)
        sqlite_uri = "sqlite:///" + db_path.replace("\\", "/")
        app.config['SQLALCHEMY_DATABASE_URI'] = sqlite_uri
        app.looger.info(f"Using resolved SQLALCHEMY_DATABASE_URI: {sqlite_uri}")

    try:
        from src.models import init_db
        init_db(app)

        db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', 'Not configured')
        app.looger.info(f"Database initialized successfully - uri={db_uri}")

    except ImportError as e:
        app.looger.error(f"Failed to import database module: {e}")
        raise
    except Exception as e:
        app.looger.error(f"Database initialization failed: {e}")
        raise

    app.looger.info("Database initialization completed")