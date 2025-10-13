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

class DevelopmentConfig(Config):
    """Development environment configuration"""
    DEBUG = True
    TESTING = False
    
    # Development-specific logging
    LOG_LEVEL = 'DEBUG'
    LOG_FILE = BASE_DIR / 'logs' / 'development.log'

class ProductionConfig(Config):
    """Production environment configuration"""
    DEBUG = False
    TESTING = False
    
    # Production-specific settings
    LOG_LEVEL = 'INFO'
    
    # Override with production database - also in instance folder
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f'sqlite:///{INSTANCE_DIR}/cwmt_prod.db'

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