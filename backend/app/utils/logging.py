import logging
import sys
from datetime import datetime
from typing import Optional
import os

def setup_logging(
    log_level: str = "INFO",
    enable_access_logs: bool = True,
    enable_metrics: bool = True,
    sentry_dsn: Optional[str] = None
):
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Configure basic logging
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(f'logs/app-{datetime.now().strftime("%Y%m%d")}.log')
        ]
    )

    # Create logger instance
    logger = logging.getLogger("triage_ai")
    
    # Add access log handler if enabled
    if enable_access_logs:
        access_handler = logging.FileHandler(f'logs/access-{datetime.now().strftime("%Y%m%d")}.log')
        access_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
        logger.addHandler(access_handler)

    return logger

# Create a global logger instance
logger = setup_logging() 