import datetime
import random
import time
import os
import boto3
from botocore.exceptions import ClientError
from configs import config
import logging

logger = logging.getLogger(__name__)

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

def upload_to_s3(file_path, s3_key):
    """Upload a file to an S3 bucket."""
    try:
        # For EC2, use IAM role credentials (no access key/secret key)
        s3_client = boto3.client('s3', region_name=config.S3_REGION)
        s3_client.upload_file(file_path, config.S3_BUCKET_NAME, s3_key)
        logger.info(f"Successfully uploaded {file_path} to s3://{config.S3_BUCKET_NAME}/{s3_key}")
        return True
    except ClientError as e:
        logger.error(f"Failed to upload {file_path} to S3: {str(e)}")
        return False
