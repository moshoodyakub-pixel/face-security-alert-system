"""
Logger Utility Module
Configures logging for the Face Security Alert System with file and console outputs.
Implements log rotation and date-based log files.
"""

import logging
import sys
import functools
from pathlib import Path
from datetime import datetime
from logging.handlers import RotatingFileHandler


def setup_logging(
    log_dir: Path = None,
    log_level: str = "INFO",
    log_to_file: bool = True,
    log_to_console: bool = True,
    max_log_size_mb: int = 10,
    backup_count: int = 5
) -> logging.Logger:
    """
    Set up logging configuration for the application.
    
    Args:
        log_dir (Path): Directory to store log files
        log_level (str): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_file (bool): Enable logging to file
        log_to_console (bool): Enable logging to console
        max_log_size_mb (int): Maximum size of a single log file in MB
        backup_count (int): Number of backup log files to keep
    
    Returns:
        logging.Logger: Configured root logger
    """
    # Create log directory if it doesn't exist
    if log_to_file:
        if log_dir is None:
            log_dir = Path("logs")
        log_dir = Path(log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)
    
    # Get root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        fmt='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # File handler with rotation
    if log_to_file:
        # Create dated log file name
        log_filename = f"face_security_{datetime.now().strftime('%Y%m%d')}.log"
        log_path = log_dir / log_filename
        
        # Rotating file handler
        file_handler = RotatingFileHandler(
            filename=log_path,
            maxBytes=max_log_size_mb * 1024 * 1024,  # Convert MB to bytes
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)  # Log everything to file
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)
        
        print(f"Logging to file: {log_path}")
    
    # Console handler
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, log_level.upper()))
        console_handler.setFormatter(simple_formatter)
        logger.addHandler(console_handler)
    
    # Log initial message
    logger.info("=" * 60)
    logger.info("Face Security Alert System - Logging initialized")
    logger.info(f"Log level: {log_level}")
    logger.info(f"Log to file: {log_to_file}")
    logger.info(f"Log to console: {log_to_console}")
    logger.info("=" * 60)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.
    
    Args:
        name (str): Name of the module (usually __name__)
    
    Returns:
        logging.Logger: Logger instance
    """
    return logging.getLogger(name)


class LoggerContextManager:
    """Context manager for temporary logging configuration."""
    
    def __init__(self, log_level: str = "INFO"):
        """
        Initialize logger context manager.
        
        Args:
            log_level (str): Temporary log level
        """
        self.log_level = log_level
        self.original_level = None
    
    def __enter__(self):
        """Save original level and set new level."""
        logger = logging.getLogger()
        self.original_level = logger.level
        logger.setLevel(getattr(logging, self.log_level.upper()))
        return logger
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Restore original log level."""
        logger = logging.getLogger()
        logger.setLevel(self.original_level)


def log_function_call(func):
    """
    Decorator to log function calls with parameters and return values.
    
    Usage:
        @log_function_call
        def my_function(arg1, arg2):
            return result
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        logger.debug(f"Calling {func.__name__}() with args={args}, kwargs={kwargs}")
        
        try:
            result = func(*args, **kwargs)
            logger.debug(f"{func.__name__}() returned: {result}")
            return result
        except Exception as e:
            logger.error(f"{func.__name__}() raised exception: {e}")
            raise
    
    return wrapper


def log_execution_time(func):
    """
    Decorator to log function execution time.
    
    Usage:
        @log_execution_time
        def slow_function():
            time.sleep(2)
    """
    import time
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        start_time = time.time()
        
        result = func(*args, **kwargs)
        
        elapsed_time = time.time() - start_time
        logger.info(f"{func.__name__}() executed in {elapsed_time:.3f} seconds")
        
        return result
    
    return wrapper


# Example usage
if __name__ == "__main__":
    # Set up logging
    logger = setup_logging(
        log_dir=Path("logs"),
        log_level="DEBUG",
        log_to_file=True,
        log_to_console=True
    )
    
    # Test different log levels
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")
    
    # Test decorator
    @log_execution_time
    def test_function():
        import time
        time.sleep(0.1)
        return "Done"
    
    result = test_function()
    
    # Test context manager
    with LoggerContextManager("WARNING"):
        logger.debug("This debug message won't show")
        logger.warning("This warning will show")
    
    logger.debug("Debug messages are back")
