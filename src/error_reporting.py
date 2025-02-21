import os
from datetime import datetime

def log_error(error_msg):
    """Log error messages to a file with timestamp."""
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    with open(os.path.join(log_dir, "error.log"), "a") as f:
        f.write(f"{datetime.now()}: {error_msg}\n")