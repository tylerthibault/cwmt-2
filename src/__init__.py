from flask import Flask
from src.utils.looger import Logger, LogLevel
from config import config
from flask_bcrypt import Bcrypt
from flask_talisman import Talisman
from src.utils.rate_limiter import limiter
import os


def create_app(config_name='development'):
    """Application factory pattern for creating Flask app instances"""
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(config[config_name])

    # Initialize logger
    init_logger(app)
    app.looger.info("------------------- Application starting up -------------------")

    # Validate required security environment variables before anything else
    _validate_security_env(app)

    # Initialize Bcrypt
    app.bcrypt = Bcrypt(app)

    # Initialize security middleware (Talisman + Limiter)
    init_security(app)

    # Initialize database
    init_database(app)

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


def _validate_security_env(app):
    """
    Ensure mandatory encryption environment variables are present.
    The application must NOT start if PII encryption keys are absent.
    """
    missing = []
    if not os.environ.get('FIELD_ENCRYPTION_KEY'):
        missing.append('FIELD_ENCRYPTION_KEY')
    if not os.environ.get('SEARCH_HASH_KEY'):
        missing.append('SEARCH_HASH_KEY')

    if missing:
        msg = (
            f"Missing required security environment variables: {', '.join(missing)}. "
            "Set these to strong random secrets before starting the application. "
            "See docs/security.md for key generation instructions."
        )
        app.looger.error(msg)
        raise RuntimeError(msg)


def init_security(app):
    """
    Configure security middleware for the application.

    - Flask-Talisman: enforces HTTPS in production, sets HTTP security headers
      (HSTS, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, etc.)
    - Flask-Limiter: applies rate limits to all routes to mitigate brute-force
      and denial-of-service attacks.
    """
    force_https = app.config.get('TALISMAN_FORCE_HTTPS', False)

    # Content-Security-Policy: restrict origins to the same host.
    # 'unsafe-inline' is avoided for scripts — Talisman injects a per-request
    # nonce that is applied to all <script> tags via content_security_policy_nonce_in.
    # Inline styles are permitted via 'unsafe-inline' because Bootstrap 5
    # generates programmatic inline styles that cannot easily be extracted.
    csp = {
        'default-src': "'self'",
        'script-src': "'self'",   # nonce added automatically by Talisman
        'style-src': ["'self'", "'unsafe-inline'"],   # Bootstrap inline styles
        'img-src': ["'self'", 'data:'],
        'font-src': "'self'",
    }

    Talisman(
        app,
        force_https=force_https,
        strict_transport_security=force_https,
        strict_transport_security_max_age=31536000,  # 1 year
        content_security_policy=csp,
        content_security_policy_nonce_in=['script-src'],
        frame_options='DENY',
        referrer_policy='strict-origin-when-cross-origin',
        session_cookie_secure=force_https,
    )

    # Rate limiter — tighter limits on authentication endpoints are applied
    # directly via the @limiter.limit() decorator in auth_controller.py.
    # The global default (100/day, 30/hour) is deliberately conservative since
    # this application handles sensitive student PII.
    limiter.default_limits = [app.config.get('RATELIMIT_DEFAULT', '100 per day;30 per hour')]
    limiter.storage_uri = app.config.get('RATELIMIT_STORAGE_URL', 'memory://')
    limiter.init_app(app)

    app.looger.info("Security middleware initialised",
                    force_https=force_https,
                    csp_enabled=True,
                    rate_limiting_enabled=True)


def init_blueprints(app):
    """Register all application blueprints"""
    app.looger.info("Blueprints initialization started")
    
    try:
        # Register main routes blueprint
        from src.controllers.routes import main_bp
        app.register_blueprint(main_bp)\
        
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