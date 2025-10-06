import logging
import colorlog
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

class Logger:
    def __init__(self, name='takas_backend'):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Prevent duplicate handlers
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        # Console handler with colors
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Color formatter for console
        console_formatter = colorlog.ColoredFormatter(
            '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            }
        )
        console_handler.setFormatter(console_formatter)
        
        # File handler for all logs
        if not os.path.exists('logs'):
            os.makedirs('logs')
        
        file_handler = RotatingFileHandler(
            'logs/takas_backend.log',
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        
        # File formatter
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        
        # Error file handler
        error_handler = RotatingFileHandler(
            'logs/errors.log',
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)
        
        # Add handlers
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(error_handler)
    
    def debug(self, message):
        self.logger.debug(message)
    
    def info(self, message):
        self.logger.info(message)
    
    def warning(self, message):
        self.logger.warning(message)
    
    def error(self, message, exc_info=None):
        self.logger.error(message, exc_info=exc_info)
    
    def critical(self, message, exc_info=None):
        self.logger.critical(message, exc_info=exc_info)
    
    def log_request(self, request, response=None, duration=None):
        """Log HTTP request details"""
        log_data = {
            'method': request.method,
            'url': request.url,
            'ip': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', 'Unknown'),
            'duration': f"{duration:.3f}s" if duration else None
        }
        
        if response:
            log_data['status_code'] = response.status_code
            log_data['response_size'] = len(response.get_data()) if hasattr(response, 'get_data') else 0
        
        self.info(f"HTTP Request: {log_data}")
    
    def log_error_with_context(self, error, context=None):
        """Log error with additional context"""
        error_info = {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context or {}
        }
        self.error(f"Error occurred: {error_info}", exc_info=True)
    
    def log_database_operation(self, operation, table, record_id=None, details=None):
        """Log database operations"""
        log_data = {
            'operation': operation,
            'table': table,
            'record_id': record_id,
            'details': details
        }
        self.info(f"Database operation: {log_data}")
    
    def log_user_action(self, user_id, action, details=None):
        """Log user actions"""
        log_data = {
            'user_id': user_id,
            'action': action,
            'timestamp': datetime.utcnow().isoformat(),
            'details': details
        }
        self.info(f"User action: {log_data}")

# Create global logger instance
logger = Logger()
