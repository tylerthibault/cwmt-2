from flask import Flask
from src.utils.logger import Logger, LogLevel
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
    app.logger.info("------------------- Application starting up -------------------")
    
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
    
    app.logger.info(f"Flask application created successfully - config={config_name}, debug={app.config['DEBUG']}")
    
    return app


def init_logger(app):
    """Initialize and attach the custom logger to the Flask app"""
    # Determine log level based on configuration
    logger = Logger(
        name="CWMT",
        log_file=app.config.get('LOG_FILE'),
        level="DEBUG"
    )
    app.logger = logger


def init_blueprints(app):
    """Register all application blueprints"""
    app.logger.info("Blueprints initialization started")
    
    try:
        # Register main routes blueprint
        from src.controllers.routes import main_bp
        app.register_blueprint(main_bp)
        
        from src.controllers.auth_controller import auth_bp
        app.register_blueprint(auth_bp)
                
        from src.controllers.users.user_controller import user_bp
        app.register_blueprint(user_bp)

        from src.controllers.users.superuser_controller import superuser_bp
        app.register_blueprint(superuser_bp)

        from src.controllers.users.user_admin_controller import user_admin_bp
        app.register_blueprint(user_admin_bp)

        from src.controllers.users.instructor_controller import instructor_bp
        app.register_blueprint(instructor_bp)

        from src.controllers.users.student_controller import student_bp
        app.register_blueprint(student_bp)

        from src.controllers.courses.payable_items import payable_items_bp
        app.register_blueprint(payable_items_bp)

        from src.controllers.courses.course_management_controller import course_management_bp
        app.register_blueprint(course_management_bp)

    except ImportError as e:
        app.logger.warning(f"Failed to import routes: {e}")
    except Exception as e:
        app.logger.error(f"Blueprint registration failed: {e}")
    
    app.logger.info("Blueprints initialization completed")


def init_database(app):
    """Initialize database connections and create tables"""
    import os
    from sqlalchemy.engine import make_url

    app.logger.info("Database initialization started")

    # Resolve and ensure sqlite DB path exists if using sqlite
    uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
    app.logger.info(f"Configured SQLALCHEMY_DATABASE_URI: {uri}")

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
        app.logger.info(f"Resolved DB absolute path: {db_path}")

        # Ensure parent directory exists before SQLAlchemy tries to open/create the DB file
        parent = os.path.dirname(db_path) or app.instance_path
        try:
            os.makedirs(parent, exist_ok=True)
            app.logger.info(f"Ensured parent directory exists: {parent}")
        except Exception as e:
            app.logger.error(f"Failed to create DB parent directory: {e}")
            raise

        # Normalize to forward slashes for the sqlite URI (especially on Windows)
        sqlite_uri = "sqlite:///" + db_path.replace("\\", "/")
        app.config['SQLALCHEMY_DATABASE_URI'] = sqlite_uri
        app.logger.info(f"Using resolved SQLALCHEMY_DATABASE_URI: {sqlite_uri}")

    try:
        from src.models import init_db
        init_db(app)

        db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', 'Not configured')
        app.logger.info(f"Database initialized successfully - uri={db_uri}")

    except ImportError as e:
        app.logger.error(f"Failed to import database module: {e}")
        raise
    except Exception as e:
        app.logger.error(f"Database initialization failed: {e}")
        raise

    app.logger.info("Database initialization completed")