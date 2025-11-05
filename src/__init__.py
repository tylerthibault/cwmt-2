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
    
    # Initialize database
    init_database(app)

    # with app.app_context():
    #     # Initialize default settings
    #     SettingsLogic.initialize_default_mail_settings()
        
    #     # Load email config from database
    #     mail_config = SettingsLogic.get_flask_mail_config()
    #     app.config.update(mail_config)
    
    # Initialize blueprints
    init_blueprints(app)
    
    app.looger.info("Flask application created successfully", 
                   config=config_name,
                   debug=app.config['DEBUG'])
    
    return app


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


        
    except ImportError as e:
        app.looger.warning("Failed to import routes", error=str(e))
    except Exception as e:
        app.looger.error("Blueprint registration failed", error=str(e))
    
    app.looger.info("Blueprints initialization completed")


def init_database(app):
    """Initialize database connections and create tables"""
    app.looger.info("Database initialization started")
    
    try:
        from src.models import init_db
        init_db(app)
        
        db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', 'Not configured')
        app.looger.info("Database initialized successfully", database_uri=db_uri)
        
    except ImportError as e:
        app.looger.error("Failed to import database module", error=str(e))
        raise
    except Exception as e:
        app.looger.error("Database initialization failed", error=str(e))
        raise
    
    app.looger.info("Database initialization completed")