"""AWS SNS service for sending OTP via SMS."""
import boto3
import logging
from typing import Optional
from src.config import Config

logger = logging.getLogger(__name__)

class SNSService:
    """Service for sending SMS via AWS SNS."""
    
    def __init__(self):
        """Initialize SNS client."""
        self.client = boto3.client(
            'sns',
            region_name=Config.AWS_REGION,
            aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY
        )
        self.topic_arn = Config.SNS_TOPIC_ARN
    
    def send_otp_sms(self, phone_number: str, otp: str) -> bool:
        """
        Send OTP via SMS to user's phone number.
        
        Args:
            phone_number: User's phone number (E.164 format)
            otp: OTP code to send
            
        Returns:
            bool: True if SMS sent successfully
        """
        try:
            message = (
                f"Your one-time password for bill payment is: {otp}. "
                f"This code will expire in 5 minutes. "
                f"Do not share this code with anyone."
            )
            
            # If topic ARN is configured, publish to topic
            if self.topic_arn:
                response = self.client.publish(
                    TopicArn=self.topic_arn,
                    Message=message,
                    Subject='Bill Payment OTP'
                )
            else:
                # Direct SMS (requires phone number in E.164 format)
                response = self.client.publish(
                    PhoneNumber=phone_number,
                    Message=message
                )
            
            logger.info(f"OTP SMS sent to {phone_number}: {response.get('MessageId')}")
            return True
        except Exception as e:
            logger.error(f"Error sending OTP SMS: {str(e)}")
            # In development, log the OTP instead of failing
            logger.info(f"DEV MODE: OTP for {phone_number} is {otp}")
            return False

