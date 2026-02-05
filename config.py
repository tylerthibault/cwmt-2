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

    # Stripe configuration (DEPRECATED - now stored in AppSettings database)
    # These are kept as fallback for backward compatibility
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
    STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY')
    STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET')
    
    # Application settings
    APP_NAME = 'CWMT Flask Application'
    APP_VERSION = '1.0.0'
    
    # Auto-seeding configuration
    AUTO_SEED = False  # Set to True in development to auto-seed on startup
    
    # Logging configuration
    LOG_FILE = None  # Set in environment-specific configs

class DevelopmentConfig(Config):
    """Development environment configuration"""
    DEBUG = True
    TESTING = False
    
    # Enable auto-seeding in development
    AUTO_SEED = True
    
    # Development-specific logging
    LOG_LEVEL = 'DEBUG'
    LOG_FILE = BASE_DIR / 'logs' / 'development.log'

class ProductionConfig(Config):
    """Production environment configuration"""
    DEBUG = False
    TESTING = False
    
    # Production-specific settings
    LOG_LEVEL = 'INFO'
    
    # Production uses MySQL database via DATABASE_URL environment variable
    # Fallback removed - DATABASE_URL must be set in production

class TestingConfig(Config):
    """Testing environment configuration"""
    DEBUG = True
    TESTING = True
    
    # Use in-memory database for testing
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    LOG_LEVEL = 'WARNING'

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


