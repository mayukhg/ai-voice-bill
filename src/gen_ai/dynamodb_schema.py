"""
DynamoDB Schema Extensions for Gen-AI Context Storage.
"""
import boto3
import logging
from src.config import Config

logger = logging.getLogger(__name__)


def create_context_tables():
    """Create DynamoDB tables for gen-AI context storage."""
    dynamodb = boto3.client(
        'dynamodb',
        region_name=Config.AWS_REGION,
        aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY
    )
    
    # Create conversation_context table
    try:
        dynamodb.create_table(
            TableName=Config.CONTEXT_TABLE,
            AttributeDefinitions=[
                {
                    'AttributeName': 'session_id',
                    'AttributeType': 'S'
                }
            ],
            KeySchema=[
                {
                    'AttributeName': 'session_id',
                    'KeyType': 'HASH'
                }
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        logger.info(f"Created table: {Config.CONTEXT_TABLE}")
    except dynamodb.exceptions.ResourceInUseException:
        logger.info(f"Table {Config.CONTEXT_TABLE} already exists")
    except Exception as e:
        logger.error(f"Error creating {Config.CONTEXT_TABLE}: {str(e)}")
    
    # Create entity_tracking table
    try:
        dynamodb.create_table(
            TableName=Config.ENTITY_TRACKING_TABLE,
            AttributeDefinitions=[
                {
                    'AttributeName': 'session_id',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'entity_id',
                    'AttributeType': 'S'
                }
            ],
            KeySchema=[
                {
                    'AttributeName': 'session_id',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': 'entity_id',
                    'KeyType': 'RANGE'
                }
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        logger.info(f"Created table: {Config.ENTITY_TRACKING_TABLE}")
    except dynamodb.exceptions.ResourceInUseException:
        logger.info(f"Table {Config.ENTITY_TRACKING_TABLE} already exists")
    except Exception as e:
        logger.error(f"Error creating {Config.ENTITY_TRACKING_TABLE}: {str(e)}")


if __name__ == '__main__':
    create_context_tables()

