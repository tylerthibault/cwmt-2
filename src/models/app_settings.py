from datetime import datetime
from flask_bcrypt import generate_password_hash, check_password_hash
from ..utils.encryption import encrypt_string, decrypt_string
from .main import db, CRUDMixin


class AppSettings(db.Model, CRUDMixin):
    """Versioned model for storing application-wide settings with history tracking.
    
    When settings are updated, the current row is soft-deleted (deleted_at set)
    and a new row is created with the updated values. This provides full audit history.
    
    Only ONE row should have deleted_at=NULL at any time (the current settings).
    """
    
    __tablename__ = 'app_settings'
    
    # Primary Key (auto-increment for versioning)
    id = db.Column(db.Integer, primary_key=True)
    
    # ===== Flask-Mail Configuration =====
    mail_server = db.Column(db.String(255), default='smtp.gmail.com')
    mail_port = db.Column(db.Integer, default=587)
    mail_use_tls = db.Column(db.Boolean, default=True)
    mail_use_ssl = db.Column(db.Boolean, default=False)
    mail_username = db.Column(db.String(255), nullable=True)
    mail_default_sender = db.Column(db.String(255), nullable=True)
    mail_max_emails = db.Column(db.Integer, nullable=True)
    mail_password_encrypted = db.Column(db.Text, nullable=True)  # Encrypted with Fernet
    
    # ===== General App Settings =====
    app_name = db.Column(db.String(100), default='CWMT')
    support_email = db.Column(db.String(255), default='support@cwmt.com')
    site_url = db.Column(db.String(255), default='https://cwmt.example.com')
    
    # ===== Course Settings =====
    default_course_capacity = db.Column(db.Integer, default=20)
    enable_waitlist = db.Column(db.Boolean, default=True)
    
    # ===== Payment Settings =====
    currency = db.Column(db.String(3), default='USD')
    tax_rate = db.Column(db.Numeric(5, 4), default=0.0)  # e.g., 0.0825 for 8.25%
    
    # ===== Audit Fields =====
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    deleted_at = db.Column(db.DateTime, nullable=True, index=True)
    deleted_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Relationships
    creator = db.relationship('User', foreign_keys=[created_by], backref='settings_created')
    deleter = db.relationship('User', foreign_keys=[deleted_by], backref='settings_archived')
    
    def __repr__(self):
        return f'<AppSettings id={self.id}>'
    
    @classmethod
    def get_settings(cls):
        """Get the current active settings instance.
        
        Returns the most recent non-deleted settings row.
        If settings don't exist, creates them with defaults.
        
        Returns:
            AppSettings instance
        """
        settings = cls.query.filter_by(deleted_at=None).order_by(cls.created_at.desc()).first()
        if not settings:
            settings = cls.initialize_defaults()
        return settings
    
    @classmethod
    def update_settings(cls, updated_by_user_id=None, **kwargs):
        """Update settings by creating a new version and soft-deleting the old one.
        
        This creates a full audit trail of all settings changes.
        
        Args:
            updated_by_user_id: ID of user making the update
            **kwargs: Settings to update
            
        Returns:
            New AppSettings instance with updated values
        """
        current_settings = cls.get_settings()
        
        # Soft-delete the current settings
        current_settings.deleted_at = datetime.utcnow()
        current_settings.deleted_by = updated_by_user_id
        db.session.add(current_settings)
        db.session.commit()  # Commit the soft-delete before creating new record
        
        # Create new settings row with updated values
        new_settings_data = current_settings.to_dict(include_sensitive=True)
        
        # Remove fields that shouldn't be copied
        for field in ['id', 'created_at', 'created_by', 'deleted_at', 'deleted_by', 'is_current', 'mail_password_configured']:
            new_settings_data.pop(field, None)
        
        # Apply updates
        for key, value in kwargs.items():
            if key in new_settings_data or hasattr(cls, key):
                new_settings_data[key] = value
        
        mail_password = new_settings_data.pop('mail_password', None)
        
        # Create new settings instance
        new_settings = cls(**new_settings_data)
        new_settings.created_by = updated_by_user_id
        new_settings.created_at = datetime.utcnow()
        
        if mail_password:
            new_settings.set_mail_password(mail_password)
        
        new_settings.save()
        
        return new_settings
    
    def set_mail_password(self, password):
        """Store mail password as plain text (no encryption for now).
        
        Args:
            password: Plain text password
        """
        if password:
            # Clean password to remove non-breaking spaces and other problematic characters
            cleaned_password = password.replace('\xa0', ' ').replace('\u2018', "'").replace('\u2019', "'")
            cleaned_password = cleaned_password.replace('\u201c', '"').replace('\u201d', '"')
            cleaned_password = cleaned_password.replace('\u2013', '-').replace('\u2014', '-')
            self.mail_password_encrypted = cleaned_password.strip()
        else:
            self.mail_password_encrypted = None
    
    def get_mail_password(self):
        """Get mail password as plain text (no decryption for now).
        
        Returns:
            str: Password or None
        """
        if self.mail_password_encrypted:
            # Clean password to ensure ASCII compatibility
            cleaned = self.mail_password_encrypted.replace('\xa0', ' ').strip()
            return cleaned
        return None
    
    def get_mail_config(self):
        """Get Flask-Mail configuration dictionary.
        
        Returns:
            Dictionary with Flask-Mail config keys
        """
        # Helper to clean strings for ASCII compatibility
        def clean_str(s):
            if not s:
                return s
            return s.replace('\xa0', ' ').strip()
        
        return {
            'MAIL_SERVER': clean_str(self.mail_server),
            'MAIL_PORT': self.mail_port,
            'MAIL_USE_TLS': self.mail_use_tls,
            'MAIL_USE_SSL': self.mail_use_ssl,
            'MAIL_USERNAME': clean_str(self.mail_username),
            'MAIL_PASSWORD': self.get_mail_password(),  # Already cleaned in getter
            'MAIL_DEFAULT_SENDER': clean_str(self.mail_default_sender) or f'{self.app_name} <{self.mail_username}>',
            'MAIL_MAX_EMAILS': self.mail_max_emails
        }
    
    def test_mail_config(self):
        """Test if mail configuration is complete.
        
        Returns:
            Tuple (is_valid, missing_fields)
        """
        required_fields = {
            'mail_server': self.mail_server,
            'mail_port': self.mail_port,
            'mail_username': self.mail_username,
            'mail_password_encrypted': self.mail_password_encrypted
        }
        
        missing = [field for field, value in required_fields.items() if not value]
        
        return (len(missing) == 0, missing)
    
    def get_url(self, path=''):
        """Generate full URL for a given path.
        
        Args:
            path: Path to append to site URL (e.g., '/login')
            
        Returns:
            Full URL string
        """
        base_url = self.site_url.rstrip('/')
        path = path.lstrip('/')
        return f'{base_url}/{path}' if path else base_url
    
    def to_dict(self, include_sensitive=False):
        """Convert settings to dictionary.
        
        Args:
            include_sensitive: Whether to include sensitive data (default: False)
            
        Returns:
            Dictionary with settings data
        """
        data = {
            'id': self.id,
            # Mail settings (excluding password)
            'mail_server': self.mail_server,
            'mail_port': self.mail_port,
            'mail_use_tls': self.mail_use_tls,
            'mail_use_ssl': self.mail_use_ssl,
            'mail_username': self.mail_username,
            'mail_default_sender': self.mail_default_sender,
            'mail_max_emails': self.mail_max_emails,
            # General settings
            'app_name': self.app_name,
            'support_email': self.support_email,
            'site_url': self.site_url,
            # Course settings
            'default_course_capacity': self.default_course_capacity,
            'enable_waitlist': self.enable_waitlist,
            # Payment settings
            'currency': self.currency,
            'tax_rate': float(self.tax_rate) if self.tax_rate else 0.0,
            # Audit
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'created_by': self.created_by,
            'deleted_at': self.deleted_at.isoformat() if self.deleted_at else None,
            'deleted_by': self.deleted_by,
            'is_current': self.deleted_at is None
        }
        
        if include_sensitive:
            data['mail_password_configured'] = bool(self.mail_password_encrypted)
            data['mail_password'] = None  # Placeholder for updates
        
        return data
    
    @classmethod
    def initialize_defaults(cls, created_by_user_id=None):
        """Initialize settings with default values if they don't exist.
        
        This should be called during application setup.
        
        Args:
            created_by_user_id: ID of user creating initial settings (optional)
        
        Returns:
            AppSettings instance
        """
        # Check if any non-deleted settings exist
        settings = cls.query.filter_by(deleted_at=None).first()
        if not settings:
            settings = cls(
                app_name='CWMT',
                support_email='support@cwmt.com',
                site_url='https://cwmt.example.com',
                mail_server='smtp.gmail.com',
                mail_port=587,
                mail_use_tls=True,
                mail_use_ssl=False,
                default_course_capacity=20,
                enable_waitlist=True,
                currency='USD',
                tax_rate=0.0,
                created_by=created_by_user_id
            )
            settings.save()
        return settings
    
    @classmethod
    def get_history(cls, limit=50):
        """Get history of all settings changes.
        
        Args:
            limit: Maximum number of history entries to return (default: 50)
        
        Returns:
            List of AppSettings instances ordered by creation date (newest first)
        """
        return cls.query.order_by(cls.created_at.desc()).limit(limit).all()
    
    @classmethod
    def get_version(cls, version_id):
        """Get a specific historical version of settings.
        
        Args:
            version_id: The ID of the settings version to retrieve
        
        Returns:
            AppSettings instance or None
        """
        return cls.query.get(version_id)
    
    @classmethod
    def restore_version(cls, version_id, restored_by_user_id=None):
        """Restore settings to a previous version.
        
        Args:
            version_id: The ID of the settings version to restore
            restored_by_user_id: ID of user performing the restore
        
        Returns:
            New AppSettings instance with restored values
        """
        version_to_restore = cls.get_version(version_id)
        if not version_to_restore:
            raise ValueError(f"Settings version {version_id} not found")
        
        # Use update_settings with the old version's data
        restore_data = version_to_restore.to_dict(include_sensitive=False)
        
        # Remove audit fields
        for field in ['id', 'created_at', 'created_by', 'deleted_at', 'deleted_by', 'is_current']:
            restore_data.pop(field, None)
        
        return cls.update_settings(updated_by_user_id=restored_by_user_id, **restore_data)
    
    def is_current(self):
        """Check if this is the current active settings version.
        
        Returns:
            Boolean indicating if this is the active version
        """
        return self.deleted_at is None
