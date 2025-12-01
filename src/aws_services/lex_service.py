"""AWS Lex service for conversational AI."""
import boto3
import logging
import json
from typing import Dict, Any, Optional
from src.config import Config

logger = logging.getLogger(__name__)

class LexService:
    """Service for interacting with AWS Lex bot."""
    
    def __init__(self):
        """Initialize Lex client."""
        self.client = boto3.client(
            'lexv2-runtime',
            region_name=Config.AWS_REGION,
            aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY
        )
        self.bot_id = None  # Will be set after bot creation
        self.bot_alias_id = None
        self.locale_id = 'en_US'
    
    def recognize_text(self, user_id: str, text: str, session_id: str) -> Dict[str, Any]:
        """
        Send user input to Lex bot for intent recognition.
        
        Args:
            user_id: Unique user identifier
            text: User's text input
            session_id: Session identifier
            
        Returns:
            dict: Lex response with intent and slots
        """
        try:
            response = self.client.recognize_text(
                botId=self.bot_id,
                botAliasId=self.bot_alias_id,
                localeId=self.locale_id,
                sessionId=session_id,
                text=text
            )
            
            logger.info(f"Lex response for user {user_id}: {response}")
            return response
        except Exception as e:
            logger.error(f"Error recognizing text with Lex: {str(e)}")
            raise
    
    def recognize_utterance(self, user_id: str, audio: bytes, session_id: str) -> Dict[str, Any]:
        """
        Send audio input to Lex bot for intent recognition.
        
        Args:
            user_id: Unique user identifier
            audio: Audio input bytes
            session_id: Session identifier
            
        Returns:
            dict: Lex response with intent and slots
        """
        try:
            response = self.client.recognize_utterance(
                botId=self.bot_id,
                botAliasId=self.bot_alias_id,
                localeId=self.locale_id,
                sessionId=session_id,
                inputStream=audio
            )
            
            logger.info(f"Lex audio response for user {user_id}: {response}")
            return response
        except Exception as e:
            logger.error(f"Error recognizing utterance with Lex: {str(e)}")
            raise
    
    def get_intent_from_response(self, lex_response: Dict[str, Any]) -> Optional[str]:
        """
        Extract intent name from Lex response.
        
        Args:
            lex_response: Response from Lex recognize_text/utterance
            
        Returns:
            str: Intent name or None
        """
        try:
            interpretations = lex_response.get('interpretations', [])
            if interpretations:
                return interpretations[0].get('intent', {}).get('name')
        except Exception as e:
            logger.error(f"Error extracting intent: {str(e)}")
        return None
    
    def get_slots_from_response(self, lex_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract slots from Lex response.
        
        Args:
            lex_response: Response from Lex recognize_text/utterance
            
        Returns:
            dict: Slots dictionary
        """
        try:
            interpretations = lex_response.get('interpretations', [])
            if interpretations:
                return interpretations[0].get('intent', {}).get('slots', {})
        except Exception as e:
            logger.error(f"Error extracting slots: {str(e)}")
        return {}
    
    def get_message_from_response(self, lex_response: Dict[str, Any]) -> str:
        """
        Extract message from Lex response.
        
        Args:
            lex_response: Response from Lex recognize_text/utterance
            
        Returns:
            str: Response message
        """
        try:
            messages = lex_response.get('messages', [])
            if messages:
                return messages[0].get('content', '')
        except Exception as e:
            logger.error(f"Error extracting message: {str(e)}")
        return "I didn't understand that. Could you please repeat?"

