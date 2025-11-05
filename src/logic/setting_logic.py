"""
Business logic for application settings management.
"""
from typing import Dict, List, Optional
from src.models.app_settings_model import AppSettings
from src.models import db
from cryptography.fernet import Fernet
import os
import logging

logger = logging.getLogger(__name__)


class SettingsLogic:
    """Handle settings CRUD operations and encryption."""
    
    @staticmethod
    def _get_encryption_key():
        """Get encryption key from environment or generate one."""
        key = b'w55s2lcaOqDIucTmhtrbk-zxYCHE3k4bEXCF2FzzJLw='
        if not key:
            logger.warning("No encryption key found. Generating temporary one.")
            key = Fernet.generate_key().decode()
        return key.encode() if isinstance(key, str) else key
    
    @staticmethod
    def _encrypt_value(value: str) -> str:
        """Encrypt sensitive setting value."""
        if not value:
            return value
        f = Fernet(SettingsLogic._get_encryption_key())
        return f.encrypt(value.encode()).decode()
    
    @staticmethod
    def _decrypt_value(encrypted_value: str) -> str:
        """Decrypt sensitive setting value."""
        if not encrypted_value:
            return encrypted_value
        f = Fernet(SettingsLogic._get_encryption_key())
        return f.decrypt(encrypted_value.encode()).decode()
    
    @staticmethod
    def get_setting(key: str) -> Optional[str]:
        """Get setting value by key, auto-decrypt if encrypted."""
        setting = AppSettings.query.filter_by(key=key).first()
        if not setting:
            return None
        
        if setting.is_encrypted and setting.value:
            return SettingsLogic._decrypt_value(setting.value)
        return setting.value
    
    @staticmethod
    def set_setting(key: str, value: str, description: str = None, 
                   category: str = 'general', is_encrypted: bool = False) -> AppSettings:
        """Create or update a setting."""
        setting = AppSettings.query.filter_by(key=key).first()
        
        # Encrypt if needed
        if is_encrypted and value:
            value = SettingsLogic._encrypt_value(value)
        
        if setting:
            setting.value = value
            if description:
                setting.description = description
            setting.category = category
            setting.is_encrypted = is_encrypted
        else:
            setting = AppSettings(
                key=key,
                value=value,
                description=description,
                category=category,
                is_encrypted=is_encrypted
            )
            db.session.add(setting)
        
        db.session.commit()
        return setting
    
    @staticmethod
    def get_settings_by_category(category: str) -> List[AppSettings]:
        """Get all settings for a category."""
        return AppSettings.query.filter_by(category=category).order_by(AppSettings.key).all()
    
    @staticmethod
    def get_flask_mail_config() -> Dict[str, any]:
        """Convert email settings to Flask-Mail config format."""
        mail_settings = SettingsLogic.get_settings_by_category('email')
        config = {}
        
        # Map database keys to Flask-Mail config keys
        setting_map = {
            'mail_server': 'MAIL_SERVER',
            'mail_port': 'MAIL_PORT',
            'mail_use_tls': 'MAIL_USE_TLS',
            'mail_use_ssl': 'MAIL_USE_SSL',
            'mail_username': 'MAIL_USERNAME',
            'mail_password': 'MAIL_PASSWORD',
            'mail_default_sender': 'MAIL_DEFAULT_SENDER',
        }
        
        for setting in mail_settings:
            if setting.key in setting_map:
                value = setting.value
                if setting.is_encrypted and value:
                    value = SettingsLogic._decrypt_value(value)
                
                # Type conversion
                if setting.key == 'mail_port':
                    value = int(value) if value else None
                elif setting.key in ['mail_use_tls', 'mail_use_ssl']:
                    value = str(value).lower() in ['true', '1', 'yes'] if value else False
                
                if value is not None and value != '':
                    config[setting_map[setting.key]] = value
        
        return config
    
    @staticmethod
    def initialize_default_mail_settings():
        """Create default email settings if they don't exist."""
        defaults = [
            ('mail_server', 'smtp.gmail.com', 'SMTP server hostname', False),
            ('mail_port', '587', 'SMTP server port', False),
            ('mail_use_tls', 'true', 'Enable TLS encryption', False),
            ('mail_use_ssl', 'false', 'Enable SSL encryption', False),
            ('mail_username', '', 'SMTP username', False),
            ('mail_password', '', 'SMTP password', True),  # Encrypted
            ('mail_default_sender', '', 'Default sender email', False),
        ]
        
        for key, value, description, is_encrypted in defaults:
            existing = AppSettings.query.filter_by(key=key).first()
            if not existing:
                SettingsLogic.set_setting(
                    key=key,
                    value=value,
                    description=description,
                    category='email',
                    is_encrypted=is_encrypted
                )