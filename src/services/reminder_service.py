"""Service for handling bill reminders (Flow 1)."""
import logging
from typing import List, Dict, Any
from datetime import datetime
from src.aws_services.polly_service import PollyService
from src.aws_services.dynamodb_service import DynamoDBService

logger = logging.getLogger(__name__)

class ReminderService:
    """Service for managing bill reminders."""
    
    def __init__(self):
        """Initialize reminder service."""
        self.polly_service = PollyService()
        self.db_service = DynamoDBService()
    
    def get_due_bills_for_user(self, user_id: str, days_ahead: int = 7) -> List[Dict[str, Any]]:
        """
        Get bills that are due for a user.
        
        Args:
            user_id: User identifier
            days_ahead: Number of days to look ahead for due bills
            
        Returns:
            list: List of due bills
        """
        try:
            due_bills = self.db_service.get_due_bills(user_id, days_ahead)
            logger.info(f"Found {len(due_bills)} due bills for user {user_id}")
            return due_bills
        except Exception as e:
            logger.error(f"Error getting due bills: {str(e)}")
            return []
    
    def generate_reminder_audio(self, bill: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate audio reminder for a bill.
        
        Args:
            bill: Bill dictionary
            
        Returns:
            dict: Audio stream and content type
        """
        try:
            message = self.polly_service.generate_reminder_message(bill)
            audio_data = self.polly_service.synthesize_speech(message)
            
            logger.info(f"Generated reminder audio for bill {bill.get('bill_id')}")
            return audio_data
        except Exception as e:
            logger.error(f"Error generating reminder audio: {str(e)}")
            raise
    
    def generate_reminder_text(self, bill: Dict[str, Any]) -> str:
        """
        Generate text reminder message for a bill.
        
        Args:
            bill: Bill dictionary
            
        Returns:
            str: Reminder message text
        """
        return self.polly_service.generate_reminder_message(bill)
    
    def get_all_reminders_for_user(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all reminders for a user with audio and text.
        
        Args:
            user_id: User identifier
            
        Returns:
            list: List of reminder dictionaries with text and audio
        """
        try:
            due_bills = self.get_due_bills_for_user(user_id)
            reminders = []
            
            for bill in due_bills:
                reminder = {
                    'bill_id': bill.get('bill_id'),
                    'bill_type': bill.get('bill_type'),
                    'amount': bill.get('amount'),
                    'due_date': bill.get('due_date'),
                    'text_message': self.generate_reminder_text(bill),
                    'bill_details': bill
                }
                reminders.append(reminder)
            
            return reminders
        except Exception as e:
            logger.error(f"Error getting reminders: {str(e)}")
            return []

