"""
Utility functions for the Brand Price Tracker
"""

import logging
from datetime import datetime
import json
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def setup_logger(name: str):
    """Setup logger for a module"""
    return logging.getLogger(name)


def save_json(data, filepath: str):
    """Save data to JSON file"""
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logging.error(f"Error saving JSON: {e}")
        return False


def load_json(filepath: str):
    """Load data from JSON file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Error loading JSON: {e}")
        return None


def get_timestamp() -> str:
    """Get current timestamp"""
    return datetime.now().isoformat()


def cache_results(data, cache_file: str, duration: int = 3600):
    """Cache results to file with expiration"""
    cache_data = {
        'timestamp': get_timestamp(),
        'duration': duration,
        'data': data
    }
    save_json(cache_data, cache_file)


def get_cached_results(cache_file: str) -> dict or None:
    """Get cached results if not expired"""
    if not os.path.exists(cache_file):
        return None
    
    cache_data = load_json(cache_file)
    if not cache_data:
        return None
    
    timestamp = datetime.fromisoformat(cache_data['timestamp'])
    duration = cache_data.get('duration', 3600)
    
    if (datetime.now() - timestamp).seconds > duration:
        os.remove(cache_file)
        return None
    
    return cache_data.get('data')
