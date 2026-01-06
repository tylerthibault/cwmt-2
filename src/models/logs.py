from datetime import datetime, timedelta
from sqlalchemy import func
from .main import db, CRUDMixin


class Log(db.Model, CRUDMixin):
    """Universal model for logging all system activities including emails, user actions, and system events."""
    
    __tablename__ = 'logs'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Log Type and Category
    log_type = db.Column(db.String(50), nullable=False, index=True)  # 'email', 'user_action', 'system', 'payment', etc.
    action = db.Column(db.String(100), nullable=False, index=True)  # 'sent', 'login', 'logout', 'created', 'updated', 'deleted', etc.
    description = db.Column(db.Text, nullable=True)  # Human-readable description of the action
    
    # Actor (who performed the action)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    
    # Target (what was acted upon)
    target_type = db.Column(db.String(50), nullable=True, index=True)  # 'user', 'course', 'payment', 'email', etc.
    target_id = db.Column(db.Integer, nullable=True, index=True)  # ID of the target object
    
    # Email-specific fields (kept for backward compatibility)
    purpose = db.Column(db.String(50), nullable=True, index=True)  # Email purpose code
    recipient_email = db.Column(db.String(255), nullable=True, index=True)
    recipient_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    subject = db.Column(db.Text, nullable=True)  # Email subject
    body_html = db.Column(db.Text, nullable=True)  # HTML body
    body_text = db.Column(db.Text, nullable=True)  # Plain text body
    template_id = db.Column(db.Integer, db.ForeignKey('email_templates.id', ondelete='SET NULL'), nullable=True)
    template_name = db.Column(db.String(200), nullable=True)
    is_test = db.Column(db.Boolean, default=False, nullable=False)
    
    # Status and Result
    status = db.Column(db.String(20), default='pending', nullable=False, index=True)  # 'success', 'failed', 'pending', 'sent', etc.
    error_message = db.Column(db.Text, nullable=True)
    
    # Additional metadata (JSON field for flexible data storage)
    extra_data = db.Column(db.JSON, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref='activity_logs')
    template = db.relationship('EmailTemplate', back_populates='email_logs')
    recipient_user = db.relationship('User', foreign_keys=[recipient_user_id], backref='emails_received')
    
    # Status constants
    STATUS_PENDING = 'pending'
    STATUS_SUCCESS = 'success'
    STATUS_SENT = 'sent'  # For email compatibility
    STATUS_FAILED = 'failed'
    
    # Log type constants
    TYPE_EMAIL = 'email'
    TYPE_USER_ACTION = 'user_action'
    TYPE_SYSTEM = 'system'
    TYPE_PAYMENT = 'payment'
    TYPE_AUTH = 'auth'
    
    def __repr__(self):
        if self.log_type == self.TYPE_EMAIL:
            return f'<Log [Email] {self.purpose} to {self.recipient_email} ({self.status})>'
        return f'<Log [{self.log_type}] {self.action} ({self.status})>'
    
    @classmethod
    def create_log(cls, log_type=None, action=None, description=None, user_id=None, 
                   target_type=None, target_id=None, status='pending', extra_data=None,
                   # Email-specific parameters for backward compatibility
                   purpose=None, recipient_email=None, subject=None, body_html=None, body_text=None,
                   template_id=None, template_name=None, recipient_user_id=None, 
                   sent_by=None, is_test=False):
        """Create a new log entry.
        
        Universal parameters:
            log_type: Type of log ('email', 'user_action', 'system', 'payment', 'auth')
            action: Action performed ('sent', 'login', 'logout', 'created', 'updated', 'deleted')
            description: Human-readable description
            user_id: ID of user who performed the action
            target_type: Type of target object
            target_id: ID of target object
            status: Status of action ('pending', 'success', 'failed')
            extra_data: Additional data as JSON
            
        Email-specific parameters (for backward compatibility):
            purpose: Email purpose code
            recipient_email: Email address of recipient
            subject: Email subject (rendered)
            body_html: HTML body (rendered)
            body_text: Plain text body (rendered)
            template_id: ID of template used
            template_name: Name of template used
            recipient_user_id: User ID if recipient is a system user
            sent_by: User ID of who triggered the send
            is_test: Whether this is a test email
            
        Returns:
            Log instance
        """
        # Handle email logs (backward compatibility)
        if purpose or recipient_email:
            log_type = cls.TYPE_EMAIL
            action = status if status in ['sent', 'failed', 'pending'] else 'sent'
            user_id = sent_by
            
        log = cls(
            log_type=log_type or cls.TYPE_SYSTEM,
            action=action or 'unknown',
            description=description,
            user_id=user_id,
            target_type=target_type,
            target_id=target_id,
            status=status,
            extra_data=extra_data,
            # Email fields
            purpose=purpose,
            recipient_email=recipient_email,
            subject=subject,
            body_html=body_html,
            body_text=body_text,
            template_id=template_id,
            template_name=template_name,
            recipient_user_id=recipient_user_id,
            is_test=is_test
        )
        return log.save()
    
    @classmethod
    def create_email_log(cls, purpose, recipient_email, subject, body_html=None, body_text=None,
                        template_id=None, template_name=None, recipient_user_id=None,
                        sent_by=None, is_test=False, status='pending'):
        """Create an email log entry (backward compatibility method).
        
        Args:
            purpose: Email purpose code
            recipient_email: Email address of recipient
            subject: Email subject (rendered)
            body_html: HTML body (rendered)
            body_text: Plain text body (rendered)
            template_id: ID of template used
            template_name: Name of template used
            recipient_user_id: User ID if recipient is a system user
            sent_by: User ID of who triggered the send
            is_test: Whether this is a test email
            status: Initial status (default: 'pending')
            
        Returns:
            Log instance
        """
        return cls.create_log(
            log_type=cls.TYPE_EMAIL,
            action=status,
            user_id=sent_by,
            purpose=purpose,
            recipient_email=recipient_email,
            subject=subject,
            body_html=body_html,
            body_text=body_text,
            template_id=template_id,
            template_name=template_name,
            recipient_user_id=recipient_user_id,
            is_test=is_test,
            status=status
        )
    
    def mark_sent(self, commit=True):
        """Mark this email as successfully sent.
        
        Args:
            commit: Whether to commit changes to database
            
        Returns:
            self
        """
        self.status = self.STATUS_SENT
        self.error_message = None
        if commit:
            db.session.commit()
        return self
    
    def mark_failed(self, error_message, commit=True):
        """Mark this email as failed with error message.
        
        Args:
            error_message: Description of the error
            commit: Whether to commit changes to database
            
        Returns:
            self
        """
        self.status = self.STATUS_FAILED
        self.error_message = error_message
        if commit:
            db.session.commit()
        return self
    
    @classmethod
    def get_by_purpose(cls, purpose, limit=100):
        """Get email logs by purpose.
        
        Args:
            purpose: Email purpose code
            limit: Maximum number of results (default: 100)
            
        Returns:
            List of Log instances
        """
        return cls.query.filter_by(log_type=cls.TYPE_EMAIL, purpose=purpose).order_by(
            cls.created_at.desc()
        ).limit(limit).all()
    
    @classmethod
    def get_by_recipient(cls, recipient_email, limit=100):
        """Get email logs by recipient email.
        
        Args:
            recipient_email: Email address of recipient
            limit: Maximum number of results (default: 100)
            
        Returns:
            List of Log instances
        """
        return cls.query.filter_by(log_type=cls.TYPE_EMAIL, recipient_email=recipient_email).order_by(
            cls.created_at.desc()
        ).limit(limit).all()
    
    @classmethod
    def get_by_status(cls, status, limit=100):
        """Get logs by status.
        
        Args:
            status: Log status ('sent', 'failed', 'pending', 'success')
            limit: Maximum number of results (default: 100)
            
        Returns:
            List of Log instances
        """
        return cls.query.filter_by(status=status).order_by(
            cls.created_at.desc()
        ).limit(limit).all()
    
    @classmethod
    def get_by_type(cls, log_type, limit=100):
        """Get logs by type.
        
        Args:
            log_type: Type of log ('email', 'user_action', 'system', etc.)
            limit: Maximum number of results (default: 100)
            
        Returns:
            List of Log instances
        """
        return cls.query.filter_by(log_type=log_type).order_by(
            cls.created_at.desc()
        ).limit(limit).all()
    
    @classmethod
    def get_failed_emails(cls, hours=24, limit=100):
        """Get failed emails within the specified time period.
        
        Args:
            hours: Number of hours to look back (default: 24)
            limit: Maximum number of results (default: 100)
            
        Returns:
            List of Log instances
        """
        since = datetime.utcnow() - timedelta(hours=hours)
        return cls.query.filter(
            cls.log_type == cls.TYPE_EMAIL,
            cls.status == cls.STATUS_FAILED,
            cls.created_at >= since
        ).order_by(cls.created_at.desc()).limit(limit).all()
    
    @classmethod
    def get_recent_logs(cls, limit=50, log_type=None):
        """Get most recent logs.
        
        Args:
            limit: Maximum number of results (default: 50)
            log_type: Optional filter by log type
            
        Returns:
            List of Log instances
        """
        query = cls.query
        if log_type:
            query = query.filter_by(log_type=log_type)
        return query.order_by(cls.created_at.desc()).limit(limit).all()
    
    @classmethod
    def search_logs(cls, log_type=None, purpose=None, recipient_email=None, status=None, 
                    is_test=None, start_date=None, end_date=None, user_id=None, 
                    target_type=None, limit=100):
        """Search logs with multiple filters.
        
        Args:
            log_type: Filter by log type ('email', 'user_action', etc.)
            purpose: Filter by email purpose code
            recipient_email: Filter by recipient email (partial match)
            status: Filter by status
            is_test: Filter by test status (for emails)
            start_date: Filter by start date (inclusive)
            end_date: Filter by end date (inclusive)
            user_id: Filter by user who performed action
            target_type: Filter by target type
            limit: Maximum number of results (default: 100)
            
        Returns:
            List of Log instances
        """
        query = cls.query
        
        if log_type:
            query = query.filter_by(log_type=log_type)
        
        if purpose:
            query = query.filter_by(purpose=purpose)
        
        if recipient_email:
            query = query.filter(cls.recipient_email.ilike(f'%{recipient_email}%'))
        
        if status:
            query = query.filter_by(status=status)
        
        if is_test is not None:
            query = query.filter_by(is_test=is_test)
        
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        if target_type:
            query = query.filter_by(target_type=target_type)
        
        if start_date:
            query = query.filter(cls.created_at >= start_date)
        
        if end_date:
            # Add one day to include the entire end_date
            end_datetime = end_date + timedelta(days=1)
            query = query.filter(cls.created_at < end_datetime)
        
        return query.order_by(cls.created_at.desc()).limit(limit).all()
    
    @classmethod
    def get_stats_by_purpose(cls, days=30):
        """Get email statistics grouped by purpose and status.
        
        Args:
            days: Number of days to look back (default: 30)
            
        Returns:
            List of tuples: (purpose, status, count)
        """
        since = datetime.utcnow() - timedelta(days=days)
        return db.session.query(
            cls.purpose,
            cls.status,
            func.count(cls.id).label('count')
        ).filter(
            cls.log_type == cls.TYPE_EMAIL,
            cls.created_at >= since
        ).group_by(
            cls.purpose,
            cls.status
        ).all()
    
    @classmethod
    def count_by_status(cls, days=30, log_type=None):
        """Get count of logs by status.
        
        Args:
            days: Number of days to look back (default: 30)
            log_type: Optional filter by log type
            
        Returns:
            Dictionary with status as key and count as value
        """
        since = datetime.utcnow() - timedelta(days=days)
        query = db.session.query(
            cls.status,
            func.count(cls.id).label('count')
        ).filter(cls.created_at >= since)
        
        if log_type:
            query = query.filter(cls.log_type == log_type)
        
        results = query.group_by(cls.status).all()
        
        return {status: count for status, count in results}
    
    def resend(self, sent_by=None):
        """Create a new log entry to resend this email.
        
        Args:
            sent_by: User ID of who triggered the resend
            
        Returns:
            New Log instance
        """
        return self.__class__.create_log(
            log_type=self.TYPE_EMAIL,
            action='sent',
            user_id=sent_by or self.user_id,
            purpose=self.purpose,
            recipient_email=self.recipient_email,
            subject=self.subject,
            body_html=self.body_html,
            body_text=self.body_text,
            template_id=self.template_id,
            template_name=self.template_name,
            recipient_user_id=self.recipient_user_id,
            is_test=self.is_test,
            status='pending'
        )
    
    def to_dict(self, include_body=False):
        """Convert log to dictionary representation.
        
        Args:
            include_body: Whether to include email body content (default: False)
            
        Returns:
            Dictionary with log data
        """
        data = {
            'id': self.id,
            'log_type': self.log_type,
            'action': self.action,
            'description': self.description,
            'user_id': self.user_id,
            'target_type': self.target_type,
            'target_id': self.target_id,
            'status': self.status,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'extra_data': self.extra_data,
        }
        
        # Add email-specific fields if it's an email log
        if self.log_type == self.TYPE_EMAIL:
            data.update({
                'purpose': self.purpose,
                'recipient_email': self.recipient_email,
                'recipient_user_id': self.recipient_user_id,
                'subject': self.subject,
                'template_id': self.template_id,
                'template_name': self.template_name,
                'is_test': self.is_test
            })
            
            if include_body:
                data['body_html'] = self.body_html
                data['body_text'] = self.body_text
        
        return data


# Backward compatibility alias
EmailLog = Log
