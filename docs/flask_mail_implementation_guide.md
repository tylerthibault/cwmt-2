# Flask-Mail Implementation Walkthrough

This guide walks you through implementing Flask-Mail in your CWMT application with a database-driven configuration system that allows super users to manage email settings through the admin interface.

## Overview

Instead of hardcoding email configuration in your Flask config files, we'll create a flexible system where:
- Email settings are stored in a database table
- Super users can modify settings through the web interface
- The application dynamically loads email configuration from the database
- Sensitive settings (like passwords) are encrypted

## Step 1: Install Dependencies

Add these packages to your `requirements.txt`:

```text
Flask-Mail==0.9.1
cryptography==41.0.7
```

Then install them:
```bash
pip install Flask-Mail cryptography
```

## Step 2: Create the App Settings Model

Create `src/models/app_settings.py`:

```python
"""
Application settings model for storing configurable values.
"""
from src.models.base_model import BaseModel
from src.models import db


class AppSettings(BaseModel):
    """
    Store application settings in database for dynamic configuration.
    """
    __tablename__ = 'app_settings'
    
    key = db.Column(db.String(100), unique=True, nullable=False, index=True)
    value = db.Column(db.Text, nullable=True)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(50), nullable=False, default='general', index=True)
    is_encrypted = db.Column(db.Boolean, default=False, nullable=False)
    
    def to_dict(self):
        """Serialize to dict, masking encrypted values for security"""
        base_dict = super().to_dict()
        base_dict.update({
            'key': self.key,
            'value': self.value if not self.is_encrypted else '***',
            'description': self.description,
            'category': self.category,
            'is_encrypted': self.is_encrypted
        })
        return base_dict
```

## Step 3: Add Model to Database Initialization

Update `src/models/__init__.py` to include the new model:

```python
# In the init_db function, add this import:
from src.models.app_settings import AppSettings
```

## Step 4: Create Settings Logic Layer

Create `src/logic/settings_logic.py`:

```python
"""
Business logic for application settings management.
"""
from typing import Dict, List, Optional
from src.models.app_settings import AppSettings
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
        key = os.environ.get('SETTINGS_ENCRYPTION_KEY')
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
```

## Step 5: Create Database Seed Script

Create `seeds/seed_app_settings.py`:

```python
"""
Seed script for application settings.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.logic.settings_logic import SettingsLogic


def seed_app_settings():
    """Initialize default application settings."""
    print("Seeding application settings...")
    
    # Initialize email settings
    SettingsLogic.initialize_default_mail_settings()
    
    # Add other general settings
    general_settings = [
        ('app_name', 'CWMT Flask Application', 'Application display name'),
        ('app_timezone', 'UTC', 'Default timezone'),
    ]
    
    for key, value, description in general_settings:
        from src.models.app_settings import AppSettings
        existing = AppSettings.query.filter_by(key=key).first()
        if not existing:
            SettingsLogic.set_setting(key, value, description, 'general')
    
    print("Settings seeded successfully!")


if __name__ == '__main__':
    from run import app
    with app.app_context():
        seed_app_settings()
```

## Step 6: Update Flask Application Configuration

Modify your `run.py` or main application file:

```python
from flask import Flask
from flask_mail import Mail
from src.logic.settings_logic import SettingsLogic

# Initialize Flask-Mail
mail = Mail()

def create_app():
    app = Flask(__name__)
    
    # Load your regular config
    app.config.from_object('config.DevelopmentConfig')
    
    # Initialize database
    from src.models import init_db
    init_db(app)
    
    with app.app_context():
        # Initialize default settings
        SettingsLogic.initialize_default_mail_settings()
        
        # Load email config from database
        mail_config = SettingsLogic.get_flask_mail_config()
        app.config.update(mail_config)
    
    # Initialize Flask-Mail
    mail.init_app(app)
    
    return app

app = create_app()
```

## Step 7: Add Super User Routes

Add these routes to `src/controllers/super_user_controller.py`:

```python
from src.logic.settings_logic import SettingsLogic
from flask import jsonify

@super_user_bp.route('/settings/email', methods=['GET'])
@super_user_required
def email_settings():
    """Display email settings page."""
    settings = SettingsLogic.get_settings_by_category('email')
    context = UserLogic.get_context(view_as='super-user')
    context.update({
        'settings': settings,
        'page_title': 'Email Settings'
    })
    return render_template('private/super_user/email_settings.html', **context)

@super_user_bp.route('/settings/email', methods=['POST'])
@super_user_required
def update_email_settings():
    """Update email settings."""
    data = request.get_json()
    
    for key, value in data.items():
        if key.startswith('mail_'):
            is_encrypted = key == 'mail_password'
            SettingsLogic.set_setting(key, value, category='email', is_encrypted=is_encrypted)
    
    # Reload mail config
    mail_config = SettingsLogic.get_flask_mail_config()
    app.config.update(mail_config)
    
    return jsonify({'message': 'Settings updated successfully'})

@super_user_bp.route('/settings/email/test', methods=['POST'])
@super_user_required
def test_email_settings():
    """Test email configuration."""
    try:
        from flask_mail import Message
        
        msg = Message(
            subject='Test Email',
            recipients=[SettingsLogic.get_setting('mail_default_sender')],
            body='This is a test email.'
        )
        mail.send(msg)
        return jsonify({'message': 'Test email sent successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

## Step 8: Create Email Settings Template

Create `src/templates/private/super_user/email_settings.html`:

```html
{% extends "bases/private.html" %}

{% block title %}Email Settings{% endblock %}

{% block content %}
<div class="container-fluid">
    <div class="card">
        <div class="card-header">
            <h4>Email Configuration</h4>
        </div>
        <div class="card-body">
            <form id="emailForm" onsubmit="updateSettings(event)">
                {% for setting in settings %}
                <div class="mb-3">
                    <label class="form-label">
                        {{ setting.key.replace('mail_', '').replace('_', ' ').title() }}
                    </label>
                    {% if setting.is_encrypted %}
                        <input type="password" class="form-control" 
                               name="{{ setting.key }}" 
                               placeholder="Enter new password to change">
                    {% elif setting.key in ['mail_use_tls', 'mail_use_ssl'] %}
                        <select class="form-select" name="{{ setting.key }}">
                            <option value="true" {% if setting.value == 'true' %}selected{% endif %}>True</option>
                            <option value="false" {% if setting.value != 'true' %}selected{% endif %}>False</option>
                        </select>
                    {% else %}
                        <input type="{{ 'number' if setting.key == 'mail_port' else 'text' }}" 
                               class="form-control" 
                               name="{{ setting.key }}" 
                               value="{{ setting.value or '' }}">
                    {% endif %}
                    {% if setting.description %}
                    <small class="text-muted">{{ setting.description }}</small>
                    {% endif %}
                </div>
                {% endfor %}
                
                <button type="submit" class="btn btn-primary">Update Settings</button>
                <button type="button" class="btn btn-success" onclick="testEmail()">Test Email</button>
            </form>
        </div>
    </div>
</div>

<script>
function updateSettings(event) {
    event.preventDefault();
    const form = document.getElementById('emailForm');
    const formData = new FormData(form);
    const data = {};
    
    for (let [key, value] of formData.entries()) {
        if (key === 'mail_password' && !value) continue; // Skip empty passwords
        data[key] = value;
    }
    
    fetch('/super/settings/email', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message || data.error);
        if (data.message) document.getElementById('mail_password').value = '';
    });
}

function testEmail() {
    fetch('/super/settings/email/test', {method: 'POST'})
    .then(response => response.json())
    .then(data => alert(data.message || data.error));
}
</script>
{% endblock %}
```

## Step 9: Set Up Environment Variables

Add to your environment (or `.env` file):

```bash
SETTINGS_ENCRYPTION_KEY=your-32-byte-base64-key-here
```

Generate a key:
```python
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
```

## Step 10: Run Database Migration

```bash
# Create the tables
python -c "from run import app; from src.models import db; app.app_context().push(); db.create_all()"

# Seed the settings
python seeds/seed_app_settings.py
```

## Step 11: Using Flask-Mail in Your Application

Now you can send emails anywhere in your app:

```python
from flask_mail import Message
from run import mail

def send_welcome_email(user_email, user_name):
    msg = Message(
        subject='Welcome to CWMT',
        recipients=[user_email],
        body=f'Welcome {user_name}!',
        html=render_template('emails/welcome.html', name=user_name)
    )
    mail.send(msg)
```

## Step 12: Email Provider Configuration Guide

This section provides detailed setup instructions for various email providers. Each provider has specific requirements and steps you need to follow.

### 🔍 **Quick Comparison: Bridge vs Standard SMTP**

| Provider | Bridge Required? | Complexity | Notes |
|----------|------------------|------------|--------|
| **ProtonMail** | ✅ **YES** | High | Must install Bridge software |
| **Gmail** | ❌ No | Low | Just needs App Password |
| **Outlook** | ❌ No | Low | Direct SMTP connection |
| **Yahoo** | ❌ No | Low | Direct SMTP connection |
| **Custom SMTP** | ❌ No | Medium | Depends on provider |

**Only ProtonMail requires Bridge software due to its end-to-end encryption!**

---

### ProtonMail Configuration

⚠️ **IMPORTANT: ProtonMail requires special Bridge software** - unlike other email providers!

ProtonMail requires special setup due to its privacy-focused approach and end-to-end encryption. **You cannot use ProtonMail with standard SMTP without the Bridge application.**

#### Why ProtonMail Needs Bridge:
- ProtonMail uses end-to-end encryption for all emails
- Standard SMTP protocols cannot handle ProtonMail's encryption
- Bridge creates a local SMTP/IMAP server that handles encryption/decryption
- **This is ONLY required for ProtonMail - other providers work directly**

#### Requirements:
1. **ProtonMail Plus or higher subscription** (Business, Professional, or Visionary)
2. **ProtonMail Bridge application** installed on your server/computer
3. **Bridge must run on the same machine as your Flask app**
4. **Custom domain** (optional but recommended for professional use)

#### Step-by-Step ProtonMail Setup:

**1. Install ProtonMail Bridge**
- Download from: https://protonmail.com/bridge
- Install on the **same machine** where your Flask app runs
- For development: Install on your local computer
- For production: Install on your production server
- Bridge creates a local SMTP/IMAP server that handles encryption

**2. Configure ProtonMail Bridge**
```bash
# Start ProtonMail Bridge
protonmail-bridge --cli

# Login with your ProtonMail credentials
# Bridge will provide local SMTP settings
```

**3. Get Bridge SMTP Settings**
After login, Bridge provides:
- **Server**: `127.0.0.1` (localhost)
- **Port**: `1025` (default SMTP port)
- **Username**: Your full ProtonMail email address
- **Password**: Generated bridge password (NOT your ProtonMail password)
- **TLS**: `true`
- **SSL**: `false`

**4. Flask-Mail Configuration for ProtonMail**
```python
# Settings to enter in your email configuration:
mail_server = "127.0.0.1"
mail_port = 1025
mail_use_tls = true
mail_use_ssl = false
mail_username = "yourusername@protonmail.com"
mail_password = "generated_bridge_password"
mail_default_sender = "yourusername@protonmail.com"
```

**5. Production Deployment Considerations**
- Install ProtonMail Bridge on your production server
- Ensure Bridge runs as a service/daemon
- Configure firewall to allow Bridge communication
- Consider using a reverse proxy for additional security

#### ProtonMail with Custom Domain:

If you have a custom domain with ProtonMail:

**1. Domain Setup**
- Add your domain in ProtonMail settings
- Configure DNS records (MX, SPF, DKIM, DMARC)
- Verify domain ownership

**2. Email Address Configuration**
```python
mail_username = "noreply@yourdomain.com"
mail_default_sender = "noreply@yourdomain.com"
# Bridge settings remain the same (localhost:1025)
```

#### Troubleshooting ProtonMail:

**Common Issues:**
1. **Bridge not running**: Ensure ProtonMail Bridge is started
2. **Wrong password**: Use Bridge-generated password, not ProtonMail password
3. **Connection refused**: Check if Bridge is listening on port 1025
4. **SSL errors**: Use TLS=true, SSL=false for Bridge

**Testing Connection:**
```bash
# Test SMTP connection manually
telnet 127.0.0.1 1025
# Should connect if Bridge is running
```

---

### Gmail Configuration

✅ **Gmail works directly with standard SMTP - NO additional software needed!**

**Requirements:**
- Gmail account
- 2-Factor Authentication enabled
- App Password generated
- **No Bridge or special software required**

#### Setup Steps:

**1. Enable 2FA**
- Go to Google Account settings
- Security → 2-Step Verification
- Enable 2FA with phone or authenticator app

**2. Generate App Password**
- Google Account → Security → App passwords
- Generate password for "Mail"
- Copy the 16-character password

**3. Gmail Settings (Enter directly in your email configuration)**
```python
mail_server = "smtp.gmail.com"
mail_port = 587
mail_use_tls = true
mail_use_ssl = false
mail_username = "youremail@gmail.com"
mail_password = "16-character-app-password"
mail_default_sender = "youremail@gmail.com"
```

**That's it! No additional software installation required.**

#### Gmail with Custom Domain (G Suite/Workspace):
```python
mail_server = "smtp.gmail.com"
mail_port = 587
mail_use_tls = true
mail_use_ssl = false
mail_username = "noreply@yourdomain.com"
mail_password = "app-password"
mail_default_sender = "noreply@yourdomain.com"
```

---

### Microsoft Outlook/Hotmail Configuration

**Requirements:**
- Outlook.com or Hotmail account
- Modern authentication enabled

#### Setup Steps:

**1. Enable SMTP in Outlook**
- Already enabled by default for most accounts
- No special configuration needed

**2. Outlook Settings**
```python
mail_server = "smtp-mail.outlook.com"
mail_port = 587
mail_use_tls = true
mail_use_ssl = false
mail_username = "youremail@outlook.com"
mail_password = "your-outlook-password"
mail_default_sender = "youremail@outlook.com"
```

#### Office 365/Microsoft 365:
```python
mail_server = "smtp.office365.com"
mail_port = 587
mail_use_tls = true
mail_use_ssl = false
mail_username = "youremail@yourdomain.com"
mail_password = "your-password-or-app-password"
mail_default_sender = "youremail@yourdomain.com"
```

---

### Yahoo Mail Configuration

**Requirements:**
- Yahoo Mail account
- App Password (if 2FA enabled)

#### Setup Steps:

**1. Generate App Password (if using 2FA)**
- Yahoo Account Info → Account Security
- Generate app password

**2. Yahoo Settings**
```python
mail_server = "smtp.mail.yahoo.com"
mail_port = 587
mail_use_tls = true
mail_use_ssl = false
mail_username = "youremail@yahoo.com"
mail_password = "your-password-or-app-password"
mail_default_sender = "youremail@yahoo.com"
```

---

### Custom SMTP Servers

For your own mail server or hosting provider:

#### Generic Settings Template:
```python
mail_server = "mail.yourdomain.com"
mail_port = 587  # or 465 for SSL, 25 for unencrypted
mail_use_tls = true  # for port 587
mail_use_ssl = false  # true for port 465
mail_username = "youremail@yourdomain.com"
mail_password = "your-password"
mail_default_sender = "youremail@yourdomain.com"
```

#### Common Hosting Providers:

**cPanel/WHM Hosting:**
```python
mail_server = "mail.yourdomain.com"
mail_port = 587
mail_use_tls = true
```

**Amazon SES:**
```python
mail_server = "email-smtp.us-east-1.amazonaws.com"
mail_port = 587
mail_use_tls = true
mail_username = "your-ses-username"
mail_password = "your-ses-password"
```

**SendGrid:**
```python
mail_server = "smtp.sendgrid.net"
mail_port = 587
mail_use_tls = true
mail_username = "apikey"
mail_password = "your-sendgrid-api-key"
```

**Mailgun:**
```python
mail_server = "smtp.mailgun.org"
mail_port = 587
mail_use_tls = true
mail_username = "postmaster@your-domain.mailgun.org"
mail_password = "your-mailgun-password"
```

---

### Development and Testing

#### Mailtrap (Recommended for Development):
```python
mail_server = "smtp.mailtrap.io"
mail_port = 2525
mail_use_tls = true
mail_use_ssl = false
mail_username = "your-mailtrap-username"
mail_password = "your-mailtrap-password"
mail_default_sender = "test@yourdomain.com"
```

#### MailHog (Local Testing):
```python
mail_server = "localhost"
mail_port = 1025
mail_use_tls = false
mail_use_ssl = false
mail_username = ""
mail_password = ""
mail_default_sender = "test@localhost"
```

#### Disable Sending (Testing Mode):
```python
mail_suppress_send = true  # Prevents actual email sending
```

---

### Security Considerations

#### General Security Tips:
1. **Always use TLS/SSL** when available
2. **Use app passwords** instead of main account passwords
3. **Limit SMTP access** by IP if possible
4. **Monitor email sending** for abuse
5. **Use environment variables** for sensitive credentials
6. **Enable logging** to track email activity

#### Production Checklist:
- [ ] SMTP credentials stored securely
- [ ] TLS/SSL enabled
- [ ] Rate limiting configured
- [ ] Monitoring and alerting set up
- [ ] Backup email configuration documented
- [ ] Email templates tested
- [ ] Spam compliance verified (SPF, DKIM, DMARC)

#### Authentication Methods Priority:
1. **App Passwords** (most secure)
2. **OAuth 2.0** (when available)
3. **Regular passwords** (least secure, avoid in production)

## Key Benefits of This Approach

1. **Dynamic Configuration**: No need to restart the app to change email settings
2. **Security**: Passwords are encrypted in the database
3. **User-Friendly**: Super users can manage settings through web interface
4. **Flexible**: Easy to add new settings categories
5. **Environment-Agnostic**: Same code works in dev/staging/production

## Next Steps

1. Add validation for email settings
2. Create email templates for common notifications
3. Add email logging and queue system for high-volume sending
4. Implement email templates management through the admin interface

This implementation gives you a robust, flexible email system that's easy to manage and maintain!