import datetime
import random
import time
import os
from configs import config

timestamp_str = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M")
log_file_name = f"log_{timestamp_str}.txt"

def log_message(message, log_file=log_file_name):
    log_dir = os.path.join(os.getcwd(), "logs")
    os.makedirs(log_dir, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"

    print(log_entry.strip())

    with open(os.path.join(log_dir, log_file), 'a') as f:
        f.write(log_entry)

def random_delay(min_seconds=0.5, max_seconds=1.0):
    """Add random delay to mimic human behavior"""
    delay = random.uniform(min_seconds, max_seconds)
    time.sleep(delay)
    return delay

def setup_directories():
    """Create necessary directory structure"""
    os.makedirs(config.BASE_DOWNLOAD_DIR, exist_ok=True)

