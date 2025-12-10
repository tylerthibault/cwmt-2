"""
Database Logger - Logs to database instead of files
Uses the Log model to store all application logs
"""
import logging
import traceback
import inspect
from datetime import datetime
from enum import Enum
from flask import has_request_context, g, session

class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class Logger:
    def __init__(self, name=None, level=LogLevel.INFO, console_output=True):
        self.name = name or "CWMT"
        self.level = level
        self.console_output = console_output
        self.formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self._setup_console_logger()
    
    def _setup_console_logger(self):
        """Configure console logger for development"""
        if not self.console_output:
            return
            
        self.console_logger = logging.getLogger(f"{self.name}_console")
        log_level = LogLevel[self.level].value if isinstance(self.level, str) else self.level.value
        self.console_logger.setLevel(getattr(logging, log_level))
        
        # Prevent duplicate handlers
        if self.console_logger.handlers:
            return
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(self.formatter)
        self.console_logger.addHandler(console_handler)
    
    def _get_caller_info(self):
        """Get information about the caller (file, function, line number)"""
        # Go up the stack to find the actual caller (skip logger methods)
        frame = inspect.currentframe()
        try:
            # Skip logger internal frames
            caller_frame = frame.f_back.f_back.f_back
            if caller_frame:
                return {
                    'module': caller_frame.f_code.co_filename.split('/')[-1].split('\\')[-1],
                    'function': caller_frame.f_code.co_name,
                    'line_number': caller_frame.f_lineno
                }
        finally:
            del frame
        
        return {'module': None, 'function': None, 'line_number': None}
    
    def _get_user_id(self):
        """Get current user ID from session if available"""
        if has_request_context():
            try:
                from src.models.logbook import Logbook
                token = session.get('token')
                if token:
                    logbook_entry = Logbook.query.filter_by(token=token, has_logged_out=False).first()
                    if logbook_entry:
                        return logbook_entry.user_id
            except:
                pass
        return None
    
    def _get_request_id(self):
        """Get current request ID if available"""
        if has_request_context():
            return getattr(g, 'request_id', None)
        return None
    
    def _log_to_database(self, level, message, exc_info=False, **kwargs):
        """Log message to database"""
        # Always log to console first
        if self.console_output:
            log_func = getattr(self.console_logger, level.lower())
            formatted_message = self._format_message(message, **kwargs)
            log_func(formatted_message)
        
        # Only attempt database logging if we're in an app context
        try:
            from flask import current_app
            
            # Check if we have an app context - if not, skip database logging
            if not current_app:
                return
                
            from src.models.logs_model import Log
            
            # Get caller information
            caller_info = self._get_caller_info()
            
            # Get exception info if requested
            exception_info = None
            if exc_info:
                exception_info = traceback.format_exc()
            
            # Get user and request context
            user_id = self._get_user_id()
            request_id = self._get_request_id()
            
            # Prepare extra data from kwargs
            extra_data = kwargs if kwargs else None
            
            # Create log entry
            Log.create_log(
                level=level,
                message=message,
                logger_name=self.name,
                module=caller_info['module'],
                function=caller_info['function'],
                line_number=caller_info['line_number'],
                exception_info=exception_info,
                user_id=user_id,
                request_id=request_id,
                extra_data=extra_data
            )
                
        except RuntimeError:
            # Working outside of application context - skip database logging
            pass
        except Exception as e:
            # Other errors during database logging
            print(f"[LOGGER ERROR] Failed to log to database: {str(e)}")
    
    def _format_message(self, message, **kwargs):
        """Add context to log messages"""
        if kwargs:
            context = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
            return f"{message} | {context}"
        return message
    
    def debug(self, message, **kwargs):
        """Log debug message"""
        self._log_to_database('DEBUG', message, **kwargs)
    
    def info(self, message, **kwargs):
        """Log info message"""
        self._log_to_database('INFO', message, **kwargs)
    
    def warning(self, message, **kwargs):
        """Log warning message"""
        self._log_to_database('WARNING', message, **kwargs)
    
    def error(self, message, exc_info=False, **kwargs):
        """Log error message with optional exception traceback"""
        self._log_to_database('ERROR', message, exc_info=exc_info, **kwargs)
    
    def critical(self, message, exc_info=False, **kwargs):
        """Log critical message with optional exception traceback"""
        self._log_to_database('CRITICAL', message, exc_info=exc_info, **kwargs)


# Create a default logger instance for module-level imports
_default_logger = Logger(name="CWMT", level=LogLevel.INFO, console_output=True)

# Module-level convenience functions
def debug(message, **kwargs):
    """Log debug message using default logger"""
    _default_logger.debug(message, **kwargs)

def info(message, **kwargs):
    """Log info message using default logger"""
    _default_logger.info(message, **kwargs)

def warning(message, **kwargs):
    """Log warning message using default logger"""
    _default_logger.warning(message, **kwargs)

def error(message, exc_info=False, **kwargs):
    """Log error message using default logger"""
    _default_logger.error(message, exc_info=exc_info, **kwargs)

def critical(message, exc_info=False, **kwargs):
    """Log critical message using default logger"""
    _default_logger.critical(message, exc_info=exc_info, **kwargs)