"""
Enhanced error handling for Alexa Skill.
Provides user-friendly error messages and logging.
"""
import logging
from typing import Dict, Any
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response
from ask_sdk_model.ui import SimpleCard
from ask_sdk_core.exceptions import AskSdkException

logger = logging.getLogger(__name__)


class ErrorHandler:
    """Handles errors and provides user-friendly responses."""
    
    ERROR_MESSAGES = {
        'ACCOUNT_NOT_LINKED': "Please link your account in the Alexa app to use this feature.",
        'BILL_NOT_FOUND': "I couldn't find that bill. Please check the bill ID and try again.",
        'PAYMENT_ERROR': "I encountered an error processing your payment. Please try again later.",
        'OTP_INVALID': "The OTP code is invalid or expired. Please request a new code.",
        'OTP_EXPIRED': "The OTP code has expired. Please initiate a new payment.",
        'NO_BILLS': "You have no bills at this time.",
        'NO_UNPAID_BILLS': "You have no unpaid bills. Great job staying on top of your payments!",
        'DATABASE_ERROR': "I'm having trouble accessing your information. Please try again in a moment.",
        'SERVICE_UNAVAILABLE': "The service is temporarily unavailable. Please try again later.",
        'INVALID_INPUT': "I didn't understand that. Please try again.",
        'TIMEOUT': "The request took too long. Please try again.",
        'GENERAL_ERROR': "Sorry, I encountered an error. Please try again later."
    }
    
    @staticmethod
    def get_error_message(error_code: str, custom_message: str = None) -> str:
        """
        Get user-friendly error message.
        
        Args:
            error_code: Error code
            custom_message: Custom message to use instead
            
        Returns:
            str: Error message
        """
        if custom_message:
            return custom_message
        return ErrorHandler.ERROR_MESSAGES.get(
            error_code,
            ErrorHandler.ERROR_MESSAGES['GENERAL_ERROR']
        )
    
    @staticmethod
    def create_error_response(
        handler_input: HandlerInput,
        error_code: str,
        custom_message: str = None,
        should_end_session: bool = True,
        reprompt_text: str = None
    ) -> Response:
        """
        Create error response for user.
        
        Args:
            handler_input: ASK handler input
            error_code: Error code
            custom_message: Custom error message
            should_end_session: Whether to end session
            reprompt_text: Reprompt text if not ending session
            
        Returns:
            Response: Error response
        """
        try:
            message = ErrorHandler.get_error_message(error_code, custom_message)
            
            # Log error
            logger.error(f"Error: {error_code} - {message}")
            
            # Create response builder
            response_builder = handler_input.response_builder
            response_builder.speak(message)
            response_builder.set_card(SimpleCard("Error", message))
            
            if should_end_session:
                response_builder.set_should_end_session(True)
            elif reprompt_text:
                response_builder.ask(reprompt_text)
            
            return response_builder.response
            
        except Exception as e:
            logger.error(f"Error creating error response: {str(e)}")
            # Fallback response
            return handler_input.response_builder.speak(
                "Sorry, I encountered an error. Please try again later."
            ).set_card(
                SimpleCard("Error", "An error occurred")
            ).set_should_end_session(True).response
    
    @staticmethod
    def handle_exception(handler_input: HandlerInput, exception: Exception) -> Response:
        """
        Handle exceptions and create appropriate response.
        
        Args:
            handler_input: ASK handler input
            exception: Exception that occurred
            
        Returns:
            Response: Error response
        """
        try:
            # Log exception
            logger.error(f"Exception occurred: {str(exception)}", exc_info=True)
            
            # Determine error code based on exception type
            error_code = 'GENERAL_ERROR'
            if isinstance(exception, ValueError):
                error_code = 'INVALID_INPUT'
            elif isinstance(exception, TimeoutError):
                error_code = 'TIMEOUT'
            elif 'database' in str(exception).lower() or 'dynamodb' in str(exception).lower():
                error_code = 'DATABASE_ERROR'
            elif 'payment' in str(exception).lower():
                error_code = 'PAYMENT_ERROR'
            
            return ErrorHandler.create_error_response(
                handler_input,
                error_code,
                should_end_session=True
            )
            
        except Exception as e:
            logger.error(f"Error in exception handler: {str(e)}")
            # Ultimate fallback
            return handler_input.response_builder.speak(
                "Sorry, I encountered an error. Please try again later."
            ).set_should_end_session(True).response
    
    @staticmethod
    def validate_user_linked(handler_input: HandlerInput) -> tuple[bool, Response | None]:
        """
        Validate that user account is linked.
        
        Args:
            handler_input: ASK handler input
            
        Returns:
            tuple: (is_linked, error_response)
        """
        from src.alexa.session_manager import SessionManager
        
        user_id = SessionManager.get_user_id(handler_input)
        if not user_id:
            error_response = ErrorHandler.create_error_response(
                handler_input,
                'ACCOUNT_NOT_LINKED',
                should_end_session=True
            )
            return False, error_response
        return True, None
    
    @staticmethod
    def handle_timeout(handler_input: HandlerInput, operation: str = "operation") -> Response:
        """
        Handle timeout errors.
        
        Args:
            handler_input: ASK handler input
            operation: Description of operation that timed out
            
        Returns:
            Response: Timeout error response
        """
        message = f"The {operation} took too long. Please try again."
        return ErrorHandler.create_error_response(
            handler_input,
            'TIMEOUT',
            custom_message=message,
            should_end_session=False,
            reprompt_text="Would you like to try again?"
        )
    
    @staticmethod
    def handle_retry(
        handler_input: HandlerInput,
        error_code: str,
        max_retries: int = 3,
        current_retry: int = 0
    ) -> Response:
        """
        Handle retry logic for failed operations.
        
        Args:
            handler_input: ASK handler input
            error_code: Error code
            max_retries: Maximum number of retries
            current_retry: Current retry count
            
        Returns:
            Response: Error response with retry option
        """
        if current_retry < max_retries:
            message = ErrorHandler.get_error_message(error_code)
            message += f" Would you like to try again?"
            
            return ErrorHandler.create_error_response(
                handler_input,
                error_code,
                custom_message=message,
                should_end_session=False,
                reprompt_text="Would you like to try again?"
            )
        else:
            return ErrorHandler.create_error_response(
                handler_input,
                error_code,
                custom_message="I've tried multiple times but couldn't complete the operation. Please try again later.",
                should_end_session=True
            )

