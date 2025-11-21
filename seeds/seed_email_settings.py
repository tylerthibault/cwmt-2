"""
Utility module for seeding email settings in the database
Provides functionality to create default email configuration on first database initialization
"""
from src.logic.setting_logic import SettingsLogic


def seed_email_settings(app):
    """
    Seed the database with default email settings.
    
    WARNING: This includes a plain-text password for development purposes only.
    Remove or change this before deploying to production.
    
    Args:
        app: Flask application instance
    """
    # Email settings - Gmail configuration
    email_settings = [
        {
            'key': 'mail_server',
            'value': 'smtp.gmail.com',
            'description': 'SMTP server address',
            'category': 'email',
            'is_encrypted': False
        },
        {
            'key': 'mail_port',
            'value': '587',
            'description': 'SMTP server port (587 for TLS, 465 for SSL)',
            'category': 'email',
            'is_encrypted': False
        },
        {
            'key': 'mail_use_tls',
            'value': 'true',
            'description': 'Use TLS encryption',
            'category': 'email',
            'is_encrypted': False
        },
        {
            'key': 'mail_use_ssl',
            'value': 'false',
            'description': 'Use SSL encryption',
            'category': 'email',
            'is_encrypted': False
        },
        {
            'key': 'mail_username',
            'value': 'thibault.solutions@gmail.com',
            'description': 'SMTP authentication username (usually your email)',
            'category': 'email',
            'is_encrypted': False
        },
        {
            'key': 'mail_password',
            'value': 'zmvz qidj wnne exbj',
            'description': 'SMTP authentication password (Gmail App Password)',
            'category': 'email',
            'is_encrypted': True
        },
        {
            'key': 'mail_default_sender',
            'value': 'thibault.solutions@gmail.com',
            'description': 'Default sender email address',
            'category': 'email',
            'is_encrypted': False
        }
    ]
    
    settings_created = 0
    settings_updated = 0
    
    for setting_data in email_settings:
        # Extract data
        key = setting_data['key']
        value = setting_data['value']
        description = setting_data.get('description', '')
        category = setting_data.get('category', 'email')
        is_encrypted = setting_data.get('is_encrypted', False)
        
        # Check if setting already exists
        existing_value = SettingsLogic.get_setting(key)
        
        if existing_value is None:
            # Create new setting
            SettingsLogic.set_setting(
                key=key,
                value=value,
                description=description,
                category=category,
                is_encrypted=is_encrypted
            )
            print(f"  ✓ Created setting: {key}")
            settings_created += 1
        else:
            # Update existing setting (in case you want to refresh values)
            SettingsLogic.set_setting(
                key=key,
                value=value,
                description=description,
                category=category,
                is_encrypted=is_encrypted
            )
            print(f"  - Updated setting: {key}")
            settings_updated += 1
    
    print(f"\n✓ Seeded {settings_created} setting(s), updated {settings_updated}")
    print("  ⚠ SECURITY: Email password in seed file - change before production!")


__all__ = ['seed_email_settings']
