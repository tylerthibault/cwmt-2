"""
Configuration settings for CWMT Flask Application
"""
import os
from pathlib import Path

# Base directory of the application
BASE_DIR = Path(__file__).parent.absolute()

# Instance folder for instance-specific files (databases, uploads, etc.)
INSTANCE_DIR = BASE_DIR / 'instance'

# Ensure instance directory exists
INSTANCE_DIR.mkdir(exist_ok=True)

class Config:
    """Base configuration class"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # Database configuration - stored in instance folder
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f'sqlite:///{INSTANCE_DIR}/cwmt.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Application settings
    APP_NAME = 'CWMT Flask Application'
    APP_VERSION = '1.0.0'

    # Logging configuration
    LOG_FILE = None  # Set in environment-specific configs

    # -----------------------------------------------------------------------
    # Session / cookie security (data in transit)
    # -----------------------------------------------------------------------
    # Prevent JavaScript access to the session cookie
    SESSION_COOKIE_HTTPONLY = True
    # SameSite=Lax protects against most CSRF attacks while preserving normal nav
    SESSION_COOKIE_SAMESITE = 'Lax'
    # Cookie name that does not reveal framework details
    SESSION_COOKIE_NAME = 'cwmt_session'

    # -----------------------------------------------------------------------
    # Flask-Limiter defaults (conservative — this app handles student PII)
    # -----------------------------------------------------------------------
    RATELIMIT_DEFAULT = '100 per day;30 per hour'
    RATELIMIT_STORAGE_URL = 'memory://'

class DevelopmentConfig(Config):
    """Development environment configuration"""
    DEBUG = True
    TESTING = False

    # Development-specific logging
    LOG_LEVEL = 'DEBUG'
    LOG_FILE = BASE_DIR / 'logs' / 'development.log'

    # In development HTTPS is not enforced so the Secure flag is off
    SESSION_COOKIE_SECURE = False
    # Talisman HTTPS redirect is disabled locally
    TALISMAN_FORCE_HTTPS = False

class ProductionConfig(Config):
    """Production environment configuration"""
    DEBUG = False
    TESTING = False

    # Production-specific settings
    LOG_LEVEL = 'INFO'

    # Override with production database - also in instance folder
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f'sqlite:///{INSTANCE_DIR}/cwmt_prod.db'

    # Secure flag requires HTTPS - must be True in production
    SESSION_COOKIE_SECURE = True
    # Talisman enforces HTTPS and sets HSTS
    TALISMAN_FORCE_HTTPS = True

class TestingConfig(Config):
    """Testing environment configuration"""
    DEBUG = True
    TESTING = True

    # Use in-memory database for testing
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    LOG_LEVEL = 'WARNING'

    SESSION_COOKIE_SECURE = False
    TALISMAN_FORCE_HTTPS = False

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}