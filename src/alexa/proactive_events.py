"""
Proactive Events API service for sending bill reminders to Alexa users.
"""
import logging
import requests
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from src.services.reminder_service import ReminderService
from src.aws_services.dynamodb_service import DynamoDBService
from src.config import Config

logger = logging.getLogger(__name__)

# Proactive Events API endpoint
PROACTIVE_EVENTS_API_URL = "https://api.amazonalexa.com/v1/proactiveEvents"

reminder_service = ReminderService()
db_service = DynamoDBService()


class ProactiveEventsService:
    """Service for sending proactive events to Alexa users."""
    
    def __init__(self):
        """Initialize proactive events service."""
        self.api_url = PROACTIVE_EVENTS_API_URL
        self.client_id = getattr(Config, 'ALEXA_CLIENT_ID', None)
        self.client_secret = getattr(Config, 'ALEXA_CLIENT_SECRET', None)
        self.access_token = None
        self.token_expiry = None
    
    def _get_access_token(self) -> Optional[str]:
        """
        Get LWA (Login with Amazon) access token for Proactive Events API.
        
        Returns:
            str: Access token or None
        """
        try:
            # Check if we have a valid token
            if self.access_token and self.token_expiry:
                if datetime.utcnow() < self.token_expiry:
                    return self.access_token
            
            # Request new token
            token_url = "https://api.amazon.com/auth/o2/token"
            data = {
                'grant_type': 'client_credentials',
                'scope': 'alexa::proactive_events',
                'client_id': self.client_id,
                'client_secret': self.client_secret
            }
            
            response = requests.post(token_url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data['access_token']
            expires_in = token_data.get('expires_in', 3600)
            self.token_expiry = datetime.utcnow().timestamp() + expires_in - 60  # 1 minute buffer
            
            logger.info("LWA access token obtained")
            return self.access_token
            
        except Exception as e:
            logger.error(f"Error getting access token: {str(e)}")
            return None
    
    def send_bill_reminder(self, user_id: str, bill: Dict[str, Any]) -> bool:
        """
        Send proactive bill reminder event to Alexa user.
        
        Args:
            user_id: User identifier (Alexa user ID)
            bill: Bill dictionary
            
        Returns:
            bool: True if successful
        """
        try:
            access_token = self._get_access_token()
            if not access_token:
                logger.error("Failed to get access token")
                return False
            
            # Get user's Alexa endpoint ID
            user = db_service.get_user(user_id)
            endpoint_id = user.get('alexa_endpoint_id') if user else None
            
            if not endpoint_id:
                logger.warning(f"No Alexa endpoint ID for user {user_id}")
                return False
            
            # Create event payload
            event = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "referenceId": f"bill-reminder-{bill.get('bill_id')}-{datetime.utcnow().timestamp()}",
                "expiryTime": (datetime.utcnow().timestamp() + 86400) * 1000,  # 24 hours
                "event": {
                    "name": "AMAZON.MessageAlert.Activated",
                    "payload": {
                        "state": {
                            "status": "UNREAD"
                        },
                        "messageGroup": {
                            "creator": {
                                "name": "Bill Payment Assistant"
                            },
                            "count": 1,
                            "urgency": "URGENT"
                        }
                    }
                },
                "localizedAttributes": [
                    {
                        "locale": "en-US",
                        "content": {
                            "billType": bill.get('bill_type', 'Bill'),
                            "amount": f"${bill.get('amount', 0):.2f}",
                            "dueDate": bill.get('due_date', ''),
                            "message": f"Your {bill.get('bill_type', 'bill')} bill of ${bill.get('amount', 0):.2f} is due on {bill.get('due_date', 'soon')}."
                        }
                    }
                ],
                "relevantAudience": {
                    "type": "Unicast",
                    "payload": {
                        "user": user_id
                    }
                }
            }
            
            # Send event
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                self.api_url,
                headers=headers,
                json=event
            )
            
            response.raise_for_status()
            logger.info(f"Proactive event sent for bill {bill.get('bill_id')} to user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending proactive event: {str(e)}")
            return False
    
    def send_bill_reminders_for_user(self, user_id: str) -> int:
        """
        Send proactive reminders for all due bills for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            int: Number of reminders sent
        """
        try:
            reminders = reminder_service.get_all_reminders_for_user(user_id)
            sent_count = 0
            
            for reminder in reminders:
                bill = reminder.get('bill_details', reminder)
                if self.send_bill_reminder(user_id, bill):
                    sent_count += 1
            
            logger.info(f"Sent {sent_count} proactive reminders to user {user_id}")
            return sent_count
            
        except Exception as e:
            logger.error(f"Error sending reminders for user {user_id}: {str(e)}")
            return 0
    
    def send_bill_reminders_batch(self, user_ids: List[str]) -> Dict[str, int]:
        """
        Send bill reminders to multiple users.
        
        Args:
            user_ids: List of user identifiers
            
        Returns:
            dict: Mapping of user_id to number of reminders sent
        """
        results = {}
        for user_id in user_ids:
            results[user_id] = self.send_bill_reminders_for_user(user_id)
        return results


# Lambda function for scheduled reminders
def lambda_handler(event, context):
    """
    Lambda handler for scheduled bill reminder events.
    This can be triggered by EventBridge/CloudWatch Events.
    """
    try:
        service = ProactiveEventsService()
        
        # Get all users with due bills
        # In production, query DynamoDB for users with bills due
        # For now, this is a placeholder
        
        logger.info("Scheduled bill reminder job started")
        # Implementation would query for users and send reminders
        
        return {
            'statusCode': 200,
            'body': json.dumps('Reminders processed')
        }
    except Exception as e:
        logger.error(f"Error in scheduled reminder: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error: {str(e)}')
        }

