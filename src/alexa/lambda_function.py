"""
AWS Lambda function handler for Alexa Skill.
This is the main entry point for all Alexa requests.
"""
import logging
import os
import json
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler, AbstractExceptionHandler
from ask_sdk_core.utils import is_request_type, is_intent_name, get_slot_value
from ask_sdk_model import Response
from ask_sdk_model.ui import SimpleCard
from ask_sdk_core.handler_input import HandlerInput

# Import existing services
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.reminder_service import ReminderService
from src.services.payment_service import PaymentService
from src.aws_services.dynamodb_service import DynamoDBService
from src.utils.helpers import validate_user_id
from src.alexa.session_manager import SessionManager
from src.alexa.error_handler import ErrorHandler

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Initialize services
reminder_service = ReminderService()
payment_service = PaymentService()
db_service = DynamoDBService()

# Skill Builder
sb = SkillBuilder()


class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for LaunchRequest - when user opens the skill."""
    
    def can_handle(self, handler_input):
        return is_request_type("LaunchRequest")(handler_input)
    
    def handle(self, handler_input):
        logger.info("LaunchRequest received")
        
        # Check if user is linked
        user_id = self._get_user_id(handler_input)
        if not user_id:
            speech_text = (
                "Welcome to Bill Payment Assistant. "
                "To use this skill, you need to link your account. "
                "Please open the Alexa app and link your account to get started."
            )
            return handler_input.response_builder.speak(speech_text).set_card(
                SimpleCard("Account Linking Required", speech_text)
            ).set_should_end_session(True).response
        
        speech_text = (
            "Welcome to Bill Payment Assistant. "
            "I can help you manage and pay your bills. "
            "You can ask me what bills are due, pay a bill, or check your payment history. "
            "What would you like to do?"
        )
        
        return handler_input.response_builder.speak(speech_text).ask(
            "What would you like to do? You can ask about bills, make a payment, or check your payment history."
        ).set_card(
            SimpleCard("Bill Payment Assistant", "Welcome! How can I help you?")
        ).response
    
    def _get_user_id(self, handler_input):
        """Extract user_id from access token or session attributes."""
        return SessionManager.get_user_id(handler_input)


class GetBillRemindersIntentHandler(AbstractRequestHandler):
    """Handler for GetBillReminders intent."""
    
    def can_handle(self, handler_input):
        return is_intent_name("GetBillReminders")(handler_input)
    
    def handle(self, handler_input):
        logger.info("GetBillReminders intent received")
        
        user_id = self._get_user_id(handler_input)
        if not user_id:
            return self._account_linking_response(handler_input)
        
        try:
            reminders = reminder_service.get_all_reminders_for_user(user_id)
            
            if not reminders:
                speech_text = "You have no bills due at this time. Great job staying on top of your payments!"
            else:
                count = len(reminders)
                first_bill = reminders[0]
                
                if count == 1:
                    speech_text = (
                        f"You have {count} bill due. "
                        f"Your {first_bill.get('bill_type', 'bill')} bill of "
                        f"${first_bill.get('amount', 0):.2f} is due on {self._format_date(first_bill.get('due_date'))}. "
                        f"Would you like to pay it now?"
                    )
                else:
                    speech_text = (
                        f"You have {count} bills due. "
                        f"Your {first_bill.get('bill_type', 'bill')} bill of "
                        f"${first_bill.get('amount', 0):.2f} is due on {self._format_date(first_bill.get('due_date'))}. "
                        f"Would you like to pay it now, or would you like to hear all your due bills?"
                    )
            
            return handler_input.response_builder.speak(speech_text).ask(
                "Would you like to pay a bill or hear more details?"
            ).set_card(
                SimpleCard("Bill Reminders", speech_text)
            ).response
            
        except Exception as e:
            logger.error(f"Error in GetBillReminders: {str(e)}")
            return self._error_response(handler_input, "Sorry, I encountered an error while getting your bills. Please try again later.")
    
    def _get_user_id(self, handler_input):
        session_attr = handler_input.attributes_manager.session_attributes
        return session_attr.get('user_id')
    
    def _format_date(self, date_str):
        """Format date string for speech."""
        if not date_str:
            return "soon"
        try:
            from datetime import datetime
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            return date_obj.strftime("%B %d")
        except:
            return date_str
    
    def _account_linking_response(self, handler_input):
        speech_text = "Please link your account in the Alexa app to use this feature."
        return handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard("Account Linking Required", speech_text)
        ).set_should_end_session(True).response
    
    def _error_response(self, handler_input, message):
        return handler_input.response_builder.speak(message).set_card(
            SimpleCard("Error", message)
        ).set_should_end_session(True).response


class PayBillIntentHandler(AbstractRequestHandler):
    """Handler for PayBill intent."""
    
    def can_handle(self, handler_input):
        return is_intent_name("PayBill")(handler_input)
    
    def handle(self, handler_input):
        logger.info("PayBill intent received")
        
        user_id = self._get_user_id(handler_input)
        if not user_id:
            return self._account_linking_response(handler_input)
        
        # Get bill_id from slot
        bill_id = get_slot_value(handler_input, "BillId")
        
        # If no bill_id, list available bills
        if not bill_id:
            try:
                bills = payment_service.get_user_bills_for_payment(user_id)
                if not bills:
                    speech_text = "You have no unpaid bills at this time."
                    return handler_input.response_builder.speak(speech_text).set_card(
                        SimpleCard("No Bills", speech_text)
                    ).set_should_end_session(True).response
                
                # Store bills in session for selection
                session_attr = handler_input.attributes_manager.session_attributes
                session_attr['available_bills'] = [b.get('bill_id') for b in bills]
                
                if len(bills) == 1:
                    bill = bills[0]
                    speech_text = (
                        f"You have one unpaid bill: {bill.get('bill_type')} for "
                        f"${bill.get('amount', 0):.2f}. Would you like to pay it?"
                    )
                    session_attr['pending_bill_id'] = bill.get('bill_id')
                else:
                    bill_list = ", ".join([f"{b.get('bill_type')} for ${b.get('amount', 0):.2f}" for b in bills[:3]])
                    speech_text = (
                        f"You have {len(bills)} unpaid bills: {bill_list}. "
                        f"Which bill would you like to pay? Please say the bill type or bill ID."
                    )
                
                return handler_input.response_builder.speak(speech_text).ask(
                    "Which bill would you like to pay?"
                ).set_card(
                    SimpleCard("Unpaid Bills", speech_text)
                ).response
                
            except Exception as e:
                logger.error(f"Error listing bills: {str(e)}")
                return self._error_response(handler_input, "Sorry, I encountered an error. Please try again.")
        
        # Initiate payment
        try:
            result = payment_service.initiate_payment(user_id, bill_id)
            
            if result['success']:
                # Store bill_id in session for OTP verification
                session_attr = handler_input.attributes_manager.session_attributes
                session_attr['pending_bill_id'] = bill_id
                session_attr['pending_payment_amount'] = result.get('amount')
                
                speech_text = result.get('message', 'OTP has been sent to your mobile number. Please provide the OTP.')
                
                return handler_input.response_builder.speak(speech_text).ask(
                    "Please provide the OTP code sent to your mobile number."
                ).set_card(
                    SimpleCard("Payment Initiated", speech_text)
                ).response
            else:
                return handler_input.response_builder.speak(
                    result.get('message', 'Sorry, I could not initiate the payment.')
                ).set_card(
                    SimpleCard("Payment Error", result.get('message', 'Payment initiation failed'))
                ).set_should_end_session(True).response
                
        except Exception as e:
            logger.error(f"Error initiating payment: {str(e)}")
            return self._error_response(handler_input, "Sorry, I encountered an error while initiating payment. Please try again later.")
    
    def _get_user_id(self, handler_input):
        session_attr = handler_input.attributes_manager.session_attributes
        return session_attr.get('user_id')
    
    def _account_linking_response(self, handler_input):
        speech_text = "Please link your account in the Alexa app to make payments."
        return handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard("Account Linking Required", speech_text)
        ).set_should_end_session(True).response
    
    def _error_response(self, handler_input, message):
        return handler_input.response_builder.speak(message).set_card(
            SimpleCard("Error", message)
        ).set_should_end_session(True).response


class VerifyOTPIntentHandler(AbstractRequestHandler):
    """Handler for VerifyOTP intent."""
    
    def can_handle(self, handler_input):
        return is_intent_name("VerifyOTP")(handler_input)
    
    def handle(self, handler_input):
        logger.info("VerifyOTP intent received")
        
        user_id = self._get_user_id(handler_input)
        if not user_id:
            return self._account_linking_response(handler_input)
        
        # Get OTP from slot
        otp = get_slot_value(handler_input, "OTP")
        
        if not otp:
            speech_text = "Please provide the OTP code sent to your mobile number."
            return handler_input.response_builder.speak(speech_text).ask(
                "What is the OTP code?"
            ).set_card(
                SimpleCard("OTP Required", speech_text)
            ).response
        
        # Get pending bill_id from session
        session_attr = handler_input.attributes_manager.session_attributes
        bill_id = session_attr.get('pending_bill_id')
        
        if not bill_id:
            speech_text = "No pending payment found. Please initiate a payment first."
            return handler_input.response_builder.speak(speech_text).set_card(
                SimpleCard("No Pending Payment", speech_text)
            ).set_should_end_session(True).response
        
        try:
            result = payment_service.verify_otp_and_pay(user_id, bill_id, otp)
            
            if result['success']:
                # Clear session attributes
                session_attr.pop('pending_bill_id', None)
                session_attr.pop('pending_payment_amount', None)
                
                speech_text = result.get('confirmation_message', result.get('message', 'Payment processed successfully'))
                
                return handler_input.response_builder.speak(speech_text).set_card(
                    SimpleCard("Payment Successful", speech_text)
                ).set_should_end_session(True).response
            else:
                speech_text = result.get('message', 'OTP verification failed. Please try again.')
                return handler_input.response_builder.speak(speech_text).ask(
                    "Please provide the correct OTP code."
                ).set_card(
                    SimpleCard("OTP Verification Failed", speech_text)
                ).response
                
        except Exception as e:
            logger.error(f"Error verifying OTP: {str(e)}")
            return self._error_response(handler_input, "Sorry, I encountered an error while processing your payment. Please try again.")
    
    def _get_user_id(self, handler_input):
        session_attr = handler_input.attributes_manager.session_attributes
        return session_attr.get('user_id')
    
    def _account_linking_response(self, handler_input):
        speech_text = "Please link your account in the Alexa app to verify payments."
        return handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard("Account Linking Required", speech_text)
        ).set_should_end_session(True).response
    
    def _error_response(self, handler_input, message):
        return handler_input.response_builder.speak(message).set_card(
            SimpleCard("Error", message)
        ).set_should_end_session(True).response


class ListBillsIntentHandler(AbstractRequestHandler):
    """Handler for ListBills intent."""
    
    def can_handle(self, handler_input):
        return is_intent_name("ListBills")(handler_input)
    
    def handle(self, handler_input):
        logger.info("ListBills intent received")
        
        user_id = self._get_user_id(handler_input)
        if not user_id:
            return self._account_linking_response(handler_input)
        
        try:
            bills = payment_service.get_user_bills_for_payment(user_id)
            
            if not bills:
                speech_text = "You have no unpaid bills at this time."
                return handler_input.response_builder.speak(speech_text).set_card(
                    SimpleCard("No Bills", speech_text)
                ).set_should_end_session(True).response
            
            if len(bills) == 1:
                bill = bills[0]
                speech_text = (
                    f"You have one unpaid bill: {bill.get('bill_type')} for "
                    f"${bill.get('amount', 0):.2f}, due on {self._format_date(bill.get('due_date'))}. "
                    f"Would you like to pay it?"
                )
            else:
                bill_list = []
                for bill in bills[:5]:  # Limit to 5 bills
                    bill_list.append(
                        f"{bill.get('bill_type')} for ${bill.get('amount', 0):.2f}"
                    )
                bill_text = ", ".join(bill_list)
                speech_text = (
                    f"You have {len(bills)} unpaid bills: {bill_text}. "
                    f"Which one would you like to pay?"
                )
            
            return handler_input.response_builder.speak(speech_text).ask(
                "Which bill would you like to pay?"
            ).set_card(
                SimpleCard("Your Bills", speech_text)
            ).response
            
        except Exception as e:
            logger.error(f"Error listing bills: {str(e)}")
            return self._error_response(handler_input, "Sorry, I encountered an error. Please try again.")
    
    def _get_user_id(self, handler_input):
        session_attr = handler_input.attributes_manager.session_attributes
        return session_attr.get('user_id')
    
    def _format_date(self, date_str):
        """Format date string for speech."""
        if not date_str:
            return "soon"
        try:
            from datetime import datetime
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            return date_obj.strftime("%B %d")
        except:
            return date_str
    
    def _account_linking_response(self, handler_input):
        speech_text = "Please link your account in the Alexa app to view your bills."
        return handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard("Account Linking Required", speech_text)
        ).set_should_end_session(True).response
    
    def _error_response(self, handler_input, message):
        return handler_input.response_builder.speak(message).set_card(
            SimpleCard("Error", message)
        ).set_should_end_session(True).response


class PaymentStatusIntentHandler(AbstractRequestHandler):
    """Handler for PaymentStatus intent."""
    
    def can_handle(self, handler_input):
        return is_intent_name("PaymentStatus")(handler_input)
    
    def handle(self, handler_input):
        logger.info("PaymentStatus intent received")
        
        user_id = self._get_user_id(handler_input)
        if not user_id:
            return self._account_linking_response(handler_input)
        
        # Get payment_id from slot if provided
        payment_id = get_slot_value(handler_input, "PaymentId")
        
        try:
            if payment_id:
                # Get specific payment
                payment = db_service.get_payment(payment_id)
                if payment and payment.get('user_id') == user_id:
                    status = payment.get('status', 'unknown')
                    amount = payment.get('amount', 0)
                    date = payment.get('payment_date', '')
                    speech_text = (
                        f"Payment {payment_id} has status {status}. "
                        f"Amount: ${amount:.2f}, Date: {self._format_date(date)}."
                    )
                else:
                    speech_text = f"Payment {payment_id} not found."
            else:
                # Get recent payments
                payments = db_service.get_user_payments(user_id, limit=5)
                if not payments:
                    speech_text = "You have no payment history."
                else:
                    speech_text = f"You have {len(payments)} recent payments. "
                    for payment in payments[:3]:
                        speech_text += (
                            f"Payment of ${payment.get('amount', 0):.2f} on "
                            f"{self._format_date(payment.get('payment_date'))}, "
                        )
                    speech_text += "Would you like to hear more details?"
            
            return handler_input.response_builder.speak(speech_text).ask(
                "Would you like to know more about any specific payment?"
            ).set_card(
                SimpleCard("Payment Status", speech_text)
            ).response
            
        except Exception as e:
            logger.error(f"Error getting payment status: {str(e)}")
            return self._error_response(handler_input, "Sorry, I encountered an error. Please try again.")
    
    def _get_user_id(self, handler_input):
        session_attr = handler_input.attributes_manager.session_attributes
        return session_attr.get('user_id')
    
    def _format_date(self, date_str):
        """Format date string for speech."""
        if not date_str:
            return "recently"
        try:
            from datetime import datetime
            if 'T' in date_str:
                date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            else:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            return date_obj.strftime("%B %d, %Y")
        except:
            return date_str
    
    def _account_linking_response(self, handler_input):
        speech_text = "Please link your account in the Alexa app to check payment status."
        return handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard("Account Linking Required", speech_text)
        ).set_should_end_session(True).response
    
    def _error_response(self, handler_input, message):
        return handler_input.response_builder.speak(message).set_card(
            SimpleCard("Error", message)
        ).set_should_end_session(True).response


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help intent."""
    
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.HelpIntent")(handler_input)
    
    def handle(self, handler_input):
        logger.info("HelpIntent received")
        
        speech_text = (
            "I can help you manage and pay your bills. Here's what you can ask me: "
            "What bills are due, pay my bill, list my bills, or check payment status. "
            "You can also say cancel or stop at any time. What would you like to do?"
        )
        
        return handler_input.response_builder.speak(speech_text).ask(
            "What would you like to do?"
        ).set_card(
            SimpleCard("Help", speech_text)
        ).response


class CancelAndStopIntentHandler(AbstractRequestHandler):
    """Handler for Cancel and Stop intents."""
    
    def can_handle(self, handler_input):
        return (is_intent_name("AMAZON.CancelIntent")(handler_input) or
                is_intent_name("AMAZON.StopIntent")(handler_input))
    
    def handle(self, handler_input):
        logger.info("Cancel/Stop intent received")
        
        speech_text = "Goodbye! Have a great day!"
        
        return handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard("Goodbye", speech_text)
        ).set_should_end_session(True).response


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for SessionEndedRequest."""
    
    def can_handle(self, handler_input):
        return is_request_type("SessionEndedRequest")(handler_input)
    
    def handle(self, handler_input):
        logger.info("Session ended")
        # Clean up session if needed
        return handler_input.response_builder.response


class FallbackIntentHandler(AbstractRequestHandler):
    """Handler for FallbackIntent."""
    
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.FallbackIntent")(handler_input)
    
    def handle(self, handler_input):
        logger.info("FallbackIntent received")
        
        speech_text = (
            "Sorry, I didn't understand that. "
            "I can help you with bills, payments, and reminders. "
            "You can ask me what bills are due, pay a bill, or check payment status. "
            "What would you like to do?"
        )
        
        return handler_input.response_builder.speak(speech_text).ask(
            "What would you like to do?"
        ).set_card(
            SimpleCard("Sorry", speech_text)
        ).response


class AllExceptionHandler(AbstractExceptionHandler):
    """Handler for all exceptions."""
    
    def can_handle(self, handler_input, exception):
        return True
    
    def handle(self, handler_input, exception):
        return ErrorHandler.handle_exception(handler_input, exception)


# Register all handlers
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(GetBillRemindersIntentHandler())
sb.add_request_handler(PayBillIntentHandler())
sb.add_request_handler(VerifyOTPIntentHandler())
sb.add_request_handler(ListBillsIntentHandler())
sb.add_request_handler(PaymentStatusIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelAndStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(FallbackIntentHandler())

sb.add_exception_handler(AllExceptionHandler())

# Lambda handler
lambda_handler = sb.lambda_handler()

