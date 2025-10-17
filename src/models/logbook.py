# Purpose of the logbook is to keep track of user activities and events within the application. This will also contain the token that will be used in session that will make sure that the user is logged in. This db table will include a foreign key to the user table as well as a timestamp for when the log was created and last updated. the last updated timestamp will get updated every time the user makes a new request to the server. This will allow us to have a timer on the session and log the user out after a certain period of inactivity. 

from src.models import db
from src.models.base_model import BaseModel
from datetime import datetime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from flask import current_app as app

# Logout timer in seconds (e.g., 6000 seconds = 100 minutes)
LOGOUT_TIMER = 6000

class Logbook(BaseModel):
    """
    Logbook database model - THIN model pattern.
    
    Contains ONLY:
    - Database schema (columns, relationships, constraints)
    - Simple serialization methods (to_dict, from_dict)
    
    Does NOT contain:
    - Business logic (belongs in src/logic/logbook_logic.py)
    - Validation (belongs in logic layer)
    - Complex calculations (belongs in logic layer)
    """
    __tablename__ = 'logbooks'
    
    # Logbook fields
    user_id = db.Column(db.Integer, ForeignKey('users.id'), nullable=False)
    token = db.Column(db.String(255), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    has_logged_out = db.Column(db.Boolean, default=False, nullable=False)
    timed_out = db.Column(db.Boolean, default=False, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="logbooks")
    
    def to_dict(self):
        """
        Serialize logbook to dictionary.
        Simple serialization only - NO business logic.
        
        Returns:
            dict: Logbook data as dictionary
        """
        data = super().to_dict()
        data.update({
            'user_id': self.user_id,
            'token': self.token,
            'created_at': self.created_at.isoformat(),
            'last_updated': self.last_updated.isoformat()
        })
        return data
    
    def __repr__(self):
        """String representation"""
        return f'<Logbook UserID: {self.user_id} Token: {self.token}>'
    
    def is_timed_out(self):
        """
            will check if the logbook has timed out based on the last updated timestamp
        """
        if (datetime.utcnow() - self.last_updated).total_seconds() > LOGOUT_TIMER:
            self.timed_out = True
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def generate_token():
        """
            will use a hash as the token for the logbook
        """
        return app.bcrypt.generate_password_hash(str(datetime.utcnow())).decode('utf-8')
    
    @staticmethod
    def sign_logbook(user_id):
        """
            will create a new logbook entry for the user and return the token
        """
        token = Logbook.generate_token()
        logbook = Logbook(user_id=user_id, token=token)
        db.session.add(logbook)
        db.session.commit()
        return token
    
    @staticmethod
    def sign_out(token):
        """
            will mark the logbook as logged out
        """
        logbook = Logbook.query.filter_by(token=token, has_logged_out=False).first()
        if logbook:
            logbook.has_logged_out = True
            if (datetime.utcnow() - logbook.last_updated).total_seconds() > LOGOUT_TIMER:
                logbook.timed_out = True
            db.session.commit()
            return True
        return False
    
