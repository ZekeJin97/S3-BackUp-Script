import os
import logging

LOG_GROUP_NAME = os.environ['LOG_GROUP_NAME']

def handler(event, context):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    for record in event['Records']:
        message = record['Sns']['Message']
        logger.info(message)
