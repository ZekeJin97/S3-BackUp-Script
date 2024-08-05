import logging
import os

log_group_name = os.environ['LOG_GROUP_NAME']

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    logger.info(f"Log event: {event}")
