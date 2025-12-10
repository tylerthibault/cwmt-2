"""
Logs Model - Database model for application logging
Stores all application logs in the database for better tracking and analysis
"""
from datetime import datetime
from src.models import db
from sqlalchemy import Index

class Log(db.Model):
    """
    Log model for storing application logs in database.
    Replaces file-based logging with database logging.
    """
    __tablename__ = 'logs'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    logger_name = db.Column(db.String(50), nullable=False, default='CWMT')
    level = db.Column(db.String(10), nullable=False, index=True)  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    message = db.Column(db.Text, nullable=False)
    module = db.Column(db.String(100))  # Module/file where log was created
    function = db.Column(db.String(100))  # Function where log was created
    line_number = db.Column(db.Integer)  # Line number where log was created
    exception_info = db.Column(db.Text)  # Stack trace for errors
    user_id = db.Column(db.Integer, nullable=True)  # Optional user context (no FK to avoid circular dependencies)
    request_id = db.Column(db.String(36))  # For tracking requests
    
    # Additional context fields
    extra_data = db.Column(db.JSON)  # JSON field for additional context
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_level_timestamp', 'level', 'timestamp'),
        Index('idx_logger_timestamp', 'logger_name', 'timestamp'),
    )
    
    def __repr__(self):
        return f'<Log {self.level} - {self.timestamp} - {self.message[:50]}>'
    
    def to_dict(self):
        """Convert log to dictionary"""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'logger_name': self.logger_name,
            'level': self.level,
            'message': self.message,
            'module': self.module,
            'function': self.function,
            'line_number': self.line_number,
            'exception_info': self.exception_info,
            'user_id': self.user_id,
            'request_id': self.request_id,
            'extra_data': self.extra_data
        }
    
    @classmethod
    def create_log(cls, level, message, logger_name='CWMT', module=None, function=None, 
                   line_number=None, exception_info=None, user_id=None, request_id=None, 
                   extra_data=None):
        """
        Create a new log entry in the database.
        
        Args:
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            message: Log message
            logger_name: Name of the logger
            module: Module/file name
            function: Function name
            line_number: Line number
            exception_info: Exception stack trace
            user_id: Optional user ID
            request_id: Optional request ID for tracking
            extra_data: Optional dictionary of extra context
        
        Returns:
            Log: The created log entry
        """
        log = cls(
            level=level,
            message=message,
            logger_name=logger_name,
            module=module,
            function=function,
            line_number=line_number,
            exception_info=exception_info,
            user_id=user_id,
            request_id=request_id,
            extra_data=extra_data
        )
        
        try:
            db.session.add(log)
            db.session.commit()
            return log
        except Exception as e:
            db.session.rollback()
            # Fallback to console if database logging fails
            print(f"Failed to log to database: {str(e)}")
            print(f"Original log: [{level}] {message}")
            return None
    
    @classmethod
    def get_recent_logs(cls, limit=100, level=None):
        """
        Get recent logs with optional level filter.
        
        Args:
            limit: Maximum number of logs to return
            level: Optional level filter (ERROR, WARNING, etc.)
        
        Returns:
            List of Log objects
        """
        query = cls.query.order_by(cls.timestamp.desc())
        
        if level:
            query = query.filter_by(level=level)
        
        return query.limit(limit).all()
    
    @classmethod
    def get_logs_by_date_range(cls, start_date, end_date, level=None):
        """
        Get logs within a date range.
        
        Args:
            start_date: Start datetime
            end_date: End datetime
            level: Optional level filter
        
        Returns:
            List of Log objects
        """
        query = cls.query.filter(
            cls.timestamp >= start_date,
            cls.timestamp <= end_date
        )
        
        if level:
            query = query.filter_by(level=level)
        
        return query.order_by(cls.timestamp.desc()).all()
    
    @classmethod
    def get_error_logs(cls, limit=50):
        """Get recent error and critical logs"""
        return cls.query.filter(
            cls.level.in_(['ERROR', 'CRITICAL'])
        ).order_by(cls.timestamp.desc()).limit(limit).all()
    
    @classmethod
    def cleanup_old_logs(cls, days=90):
        """
        Delete logs older than specified days.
        Useful for log retention policies.
        
        Args:
            days: Number of days to keep logs
        
        Returns:
            Number of deleted logs
        """
        from datetime import timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        old_logs = cls.query.filter(cls.timestamp < cutoff_date)
        count = old_logs.count()
        old_logs.delete()
        db.session.commit()
        
        return count
