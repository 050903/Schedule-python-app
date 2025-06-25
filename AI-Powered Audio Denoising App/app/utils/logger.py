import logging
import os
import sys
from datetime import datetime

def setup_logging():
    """Configures the application-wide logging."""
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    log_filename = datetime.now().strftime("app_%Y%m%d_%H%M%S.log")
    log_filepath = os.path.join(log_dir, log_filename)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filepath),
            logging.StreamHandler(sys.stdout) # Also log to console
        ]
    )
    # Optionally set a higher level for specific noisy libraries
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    logging.getLogger('librosa').setLevel(logging.WARNING)
    logging.getLogger('numba').setLevel(logging.WARNING)