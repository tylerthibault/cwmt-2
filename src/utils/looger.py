import logging
import os
from datetime import datetime
from enum import Enum
from pathlib import Path

class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class Logger:
    def __init__(self, name=None, log_file=None, level=LogLevel.INFO):
        self.name = name or "CWMT"
        self.log_file_template = log_file  # Store the base log file path
        self.level = level
        self.current_date = None
        self.file_handler = None
        self.formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self._setup_logger()
    
    def _setup_logger(self):
        """Configure the logger with formatters and handlers"""
        self.logger = logging.getLogger(self.name)
        log_level = LogLevel[self.level].value
        self.logger.setLevel(getattr(logging, log_level))
        
        # Prevent duplicate handlers
        if self.logger.handlers:
            return
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(self.formatter)
        self.logger.addHandler(console_handler)
        
        # File handler will be created/updated on first log message
        if self.log_file_template:
            self._update_file_handler()
    
    def _get_daily_log_file(self):
        """Generate log file path with current date"""
        if not self.log_file_template:
            return None
        
        # Get current date in YYYY-MM-DD format
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Parse the log file template
        log_path = Path(self.log_file_template)
        log_dir = log_path.parent
        log_name = log_path.stem  # filename without extension
        log_ext = log_path.suffix  # .log
        
        # Create daily log file name: e.g., development_2025-10-12.log
        daily_log_file = log_dir / f"{today}{log_ext}"
        
        return daily_log_file
    
    def _update_file_handler(self):
        """Update file handler if date has changed"""
        today = datetime.now().date()
        
        # Check if we need to create a new file handler
        if self.current_date != today:
            # Remove old file handler if it exists
            if self.file_handler:
                self.logger.removeHandler(self.file_handler)
                self.file_handler.close()
            
            # Get the daily log file path
            daily_log_file = self._get_daily_log_file()
            
            if daily_log_file:
                # Ensure the directory exists
                daily_log_file.parent.mkdir(parents=True, exist_ok=True)
                
                # Create new file handler with daily log file
                self.file_handler = logging.FileHandler(daily_log_file)
                self.file_handler.setFormatter(self.formatter)
                self.logger.addHandler(self.file_handler)
                
                # Update current date
                self.current_date = today
    
    def _log_with_date_check(self, log_func, message, **kwargs):
        """Internal method to check date before logging"""
        # Update file handler if date has changed
        if self.log_file_template:
            self._update_file_handler()
        
        # Log the message
        log_func(self._format_message(message, **kwargs))
    
    def debug(self, message, **kwargs):
        """Log debug message"""
        self._log_with_date_check(self.logger.debug, message, **kwargs)
    
    def info(self, message, **kwargs):
        """Log info message"""
        self._log_with_date_check(self.logger.info, message, **kwargs)
    
    def warning(self, message, **kwargs):
        """Log warning message"""
        self._log_with_date_check(self.logger.warning, message, **kwargs)
    
    def error(self, message, error=None, **kwargs):
        """Log error message with optional exception"""
        formatted_message = self._format_message(message, **kwargs)
        if error:
            formatted_message += f" | Exception: {str(error)}"
        
        # Update file handler if date has changed
        if self.log_file_template:
            self._update_file_handler()
        
        self.logger.error(formatted_message)
    
    def critical(self, message, **kwargs):
        """Log critical message"""
        self._log_with_date_check(self.logger.critical, message, **kwargs)
    
    def _format_message(self, message, **kwargs):
        """Add context to log messages"""
        if kwargs:
            context = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
            return f"{message} | {context}"
        return message
    
    @classmethod
    def get_app_logger(cls):
        """Get application-wide logger instance"""
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        log_file = os.path.join(log_dir, f"cwmt_{datetime.now().strftime('%Y%m%d')}.log")
        return cls(name="CWMT", log_file=log_file)