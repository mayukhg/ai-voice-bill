"""AWS Polly service for text-to-speech conversion."""
import boto3
import logging
from typing import Optional
from src.config import Config

logger = logging.getLogger(__name__)

class PollyService:
    """Service for generating speech from text using AWS Polly."""
    
    def __init__(self):
        """Initialize Polly client."""
        self.client = boto3.client(
            'polly',
            region_name=Config.AWS_REGION,
            aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY
        )
        self.voice_id = Config.POLLY_VOICE_ID
        self.engine = Config.POLLY_ENGINE
    
    def synthesize_speech(self, text: str, voice_id: Optional[str] = None) -> dict:
        """
        Convert text to speech using AWS Polly.
        
        Args:
            text: Text to convert to speech
            voice_id: Optional voice ID (defaults to configured voice)
            
        Returns:
            dict: Response containing audio stream and content type
        """
        try:
            voice = voice_id or self.voice_id
            
            response = self.client.synthesize_speech(
                Text=text,
                OutputFormat='mp3',
                VoiceId=voice,
                Engine=self.engine
            )
            
            logger.info(f"Successfully synthesized speech for text: {text[:50]}...")
            return {
                'audio_stream': response['AudioStream'].read(),
                'content_type': response['ContentType']
            }
        except Exception as e:
            logger.error(f"Error synthesizing speech: {str(e)}")
            raise
    
    def generate_reminder_message(self, bill: dict) -> str:
        """
        Generate a personalized reminder message for a bill.
        
        Args:
            bill: Bill dictionary containing bill details
            
        Returns:
            str: Formatted reminder message
        """
        bill_type = bill.get('bill_type', 'bill')
        amount = bill.get('amount', 0)
        due_date = bill.get('due_date', '')
        
        message = (
            f"Hello! This is a reminder that you have a {bill_type} bill "
            f"of ${amount:.2f} due on {due_date}. "
            f"You can pay this bill by saying 'Pay my bills' or 'I want to pay my bills'. "
            f"Thank you for using our service!"
        )
        
        return message
    
    def generate_payment_confirmation(self, payment: dict) -> str:
        """
        Generate a payment confirmation message.
        
        Args:
            payment: Payment dictionary containing payment details
            
        Returns:
            str: Formatted confirmation message
        """
        amount = payment.get('amount', 0)
        bill_type = payment.get('bill_type', 'bill')
        
        message = (
            f"Your payment of ${amount:.2f} for your {bill_type} bill "
            f"has been successfully processed. "
            f"A confirmation has been sent to your registered email and mobile number. "
            f"Thank you for your payment!"
        )
        
        return message
    
    def generate_otp_prompt(self) -> str:
        """Generate a prompt asking for OTP."""
        return (
            "For security purposes, please provide the one-time password "
            "that was sent to your registered mobile number. "
            "You can say the OTP digits one by one, or all at once."
        )

