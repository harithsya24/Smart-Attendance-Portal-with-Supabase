# Attendence/utils.py
from datetime import datetime
import pytz
from .logger import get_logger

logger = get_logger(__name__)

def current_est_date():
    """Returns the current date in Eastern Standard Time (EST)"""
    try:
        est = pytz.timezone("America/New_York")
        return datetime.now(est).strftime("%Y-%m-%d")
    except Exception as e:
        logger.error(f"Error getting current EST date: {e}")
        return datetime.now().strftime("%Y-%m-%d")