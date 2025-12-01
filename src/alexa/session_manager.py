"""
Session management utilities for Alexa Skill.
Handles session attributes, persistent attributes, and user context.
"""
import logging
from typing import Dict, Any, Optional
from ask_sdk_core.handler_input import HandlerInput
from datetime import datetime

logger = logging.getLogger(__name__)


class SessionManager:
    """Manages session and persistent attributes for Alexa Skill."""
    
    @staticmethod
    def get_user_id(handler_input: HandlerInput) -> Optional[str]:
        """
        Extract user_id from handler input.
        Tries multiple sources: access token, session attributes, persistent attributes.
        
        Args:
            handler_input: ASK handler input
            
        Returns:
            str: User ID or None
        """
        try:
            # Try access token first (from account linking)
            access_token = handler_input.request_envelope.context.system.user.access_token
            if access_token:
                # In production, decode and validate token to get user_id
                # For now, we'll check session attributes
                pass
            
            # Try session attributes
            session_attr = handler_input.attributes_manager.session_attributes
            user_id = session_attr.get('user_id')
            if user_id:
                return user_id
            
            # Try persistent attributes
            persistent_attr = handler_input.attributes_manager.persistent_attributes
            user_id = persistent_attr.get('user_id')
            if user_id:
                # Store in session for faster access
                session_attr['user_id'] = user_id
                handler_input.attributes_manager.session_attributes = session_attr
                return user_id
            
            # Try Alexa user ID as fallback (for testing)
            alexa_user_id = handler_input.request_envelope.context.system.user.user_id
            if alexa_user_id:
                logger.warning(f"Using Alexa user ID as fallback: {alexa_user_id}")
                return alexa_user_id
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting user_id: {str(e)}")
            return None
    
    @staticmethod
    def set_user_id(handler_input: HandlerInput, user_id: str) -> bool:
        """
        Store user_id in session and persistent attributes.
        
        Args:
            handler_input: ASK handler input
            user_id: User identifier
            
        Returns:
            bool: True if successful
        """
        try:
            # Store in session
            session_attr = handler_input.attributes_manager.session_attributes
            session_attr['user_id'] = user_id
            handler_input.attributes_manager.session_attributes = session_attr
            
            # Store in persistent attributes
            persistent_attr = handler_input.attributes_manager.persistent_attributes
            persistent_attr['user_id'] = user_id
            handler_input.attributes_manager.save_persistent_attributes()
            
            return True
        except Exception as e:
            logger.error(f"Error setting user_id: {str(e)}")
            return False
    
    @staticmethod
    def get_session_attribute(handler_input: HandlerInput, key: str, default: Any = None) -> Any:
        """
        Get a session attribute value.
        
        Args:
            handler_input: ASK handler input
            key: Attribute key
            default: Default value if not found
            
        Returns:
            Any: Attribute value or default
        """
        try:
            session_attr = handler_input.attributes_manager.session_attributes
            return session_attr.get(key, default)
        except Exception as e:
            logger.error(f"Error getting session attribute: {str(e)}")
            return default
    
    @staticmethod
    def set_session_attribute(handler_input: HandlerInput, key: str, value: Any) -> bool:
        """
        Set a session attribute value.
        
        Args:
            handler_input: ASK handler input
            key: Attribute key
            value: Attribute value
            
        Returns:
            bool: True if successful
        """
        try:
            session_attr = handler_input.attributes_manager.session_attributes
            session_attr[key] = value
            handler_input.attributes_manager.session_attributes = session_attr
            return True
        except Exception as e:
            logger.error(f"Error setting session attribute: {str(e)}")
            return False
    
    @staticmethod
    def clear_session(handler_input: HandlerInput) -> bool:
        """
        Clear all session attributes.
        
        Args:
            handler_input: ASK handler input
            
        Returns:
            bool: True if successful
        """
        try:
            handler_input.attributes_manager.session_attributes = {}
            return True
        except Exception as e:
            logger.error(f"Error clearing session: {str(e)}")
            return False
    
    @staticmethod
    def get_pending_payment(handler_input: HandlerInput) -> Optional[Dict[str, Any]]:
        """
        Get pending payment information from session.
        
        Args:
            handler_input: ASK handler input
            
        Returns:
            dict: Pending payment info or None
        """
        try:
            session_attr = handler_input.attributes_manager.session_attributes
            bill_id = session_attr.get('pending_bill_id')
            amount = session_attr.get('pending_payment_amount')
            
            if bill_id:
                return {
                    'bill_id': bill_id,
                    'amount': amount
                }
            return None
        except Exception as e:
            logger.error(f"Error getting pending payment: {str(e)}")
            return None
    
    @staticmethod
    def set_pending_payment(handler_input: HandlerInput, bill_id: str, amount: float) -> bool:
        """
        Store pending payment information in session.
        
        Args:
            handler_input: ASK handler input
            bill_id: Bill identifier
            amount: Payment amount
            
        Returns:
            bool: True if successful
        """
        try:
            session_attr = handler_input.attributes_manager.session_attributes
            session_attr['pending_bill_id'] = bill_id
            session_attr['pending_payment_amount'] = amount
            session_attr['pending_payment_timestamp'] = datetime.utcnow().isoformat()
            handler_input.attributes_manager.session_attributes = session_attr
            return True
        except Exception as e:
            logger.error(f"Error setting pending payment: {str(e)}")
            return False
    
    @staticmethod
    def clear_pending_payment(handler_input: HandlerInput) -> bool:
        """
        Clear pending payment information from session.
        
        Args:
            handler_input: ASK handler input
            
        Returns:
            bool: True if successful
        """
        try:
            session_attr = handler_input.attributes_manager.session_attributes
            session_attr.pop('pending_bill_id', None)
            session_attr.pop('pending_payment_amount', None)
            session_attr.pop('pending_payment_timestamp', None)
            handler_input.attributes_manager.session_attributes = session_attr
            return True
        except Exception as e:
            logger.error(f"Error clearing pending payment: {str(e)}")
            return False
    
    @staticmethod
    def get_conversation_state(handler_input: HandlerInput) -> str:
        """
        Get current conversation state.
        
        Args:
            handler_input: ASK handler input
            
        Returns:
            str: Conversation state (e.g., 'WAITING_FOR_OTP', 'IDLE')
        """
        try:
            session_attr = handler_input.attributes_manager.session_attributes
            return session_attr.get('conversation_state', 'IDLE')
        except Exception as e:
            logger.error(f"Error getting conversation state: {str(e)}")
            return 'IDLE'
    
    @staticmethod
    def set_conversation_state(handler_input: HandlerInput, state: str) -> bool:
        """
        Set conversation state.
        
        Args:
            handler_input: ASK handler input
            state: Conversation state
            
        Returns:
            bool: True if successful
        """
        try:
            session_attr = handler_input.attributes_manager.session_attributes
            session_attr['conversation_state'] = state
            handler_input.attributes_manager.session_attributes = session_attr
            return True
        except Exception as e:
            logger.error(f"Error setting conversation state: {str(e)}")
            return False
    
    @staticmethod
    def log_session_info(handler_input: HandlerInput) -> None:
        """
        Log session information for debugging.
        
        Args:
            handler_input: ASK handler input
        """
        try:
            session_attr = handler_input.attributes_manager.session_attributes
            user_id = SessionManager.get_user_id(handler_input)
            logger.info(f"Session info - User ID: {user_id}, State: {session_attr.get('conversation_state', 'IDLE')}")
        except Exception as e:
            logger.error(f"Error logging session info: {str(e)}")

