import os
import logging
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

def log_error(error_msg):
    """Log error messages using Python's logging module."""
    logger.error(error_msg)