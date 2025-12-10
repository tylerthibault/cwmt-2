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