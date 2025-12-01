"""Service for handling bill payments with OTP MFA (Flow 2)."""
import logging
import secrets
import string
from typing import Dict, Any, Optional, List
from datetime import datetime
from src.aws_services.polly_service import PollyService
from src.aws_services.dynamodb_service import DynamoDBService
from src.aws_services.sns_service import SNSService
from src.config import Config

logger = logging.getLogger(__name__)

class PaymentService:
    """Service for managing bill payments with OTP authentication."""
    
    def __init__(self):
        """Initialize payment service."""
        self.polly_service = PollyService()
        self.db_service = DynamoDBService()
        self.sns_service = SNSService()
    
    def generate_otp(self, length: int = None) -> str:
        """
        Generate a random OTP code.
        
        Args:
            length: Length of OTP (defaults to config value)
            
        Returns:
            str: OTP code
        """
        length = length or Config.OTP_LENGTH
        digits = string.digits
        return ''.join(secrets.choice(digits) for _ in range(length))
    
    def initiate_payment(self, user_id: str, bill_id: str) -> Dict[str, Any]:
        """
        Initiate payment process for a bill.
        
        Args:
            user_id: User identifier
            bill_id: Bill identifier
            
        Returns:
            dict: Payment initiation response
        """
        try:
            # Get bill details
            bill = self.db_service.get_bill_by_id(user_id, bill_id)
            if not bill:
                return {
                    'success': False,
                    'message': 'Bill not found'
                }
            
            if bill.get('is_paid', False):
                return {
                    'success': False,
                    'message': 'This bill has already been paid'
                }
            
            # Get user details for phone number
            user = self.db_service.get_user(user_id)
            if not user:
                return {
                    'success': False,
                    'message': 'User not found'
                }
            
            phone_number = user.get('phone_number')
            if not phone_number:
                return {
                    'success': False,
                    'message': 'Phone number not registered'
                }
            
            # Generate and send OTP
            otp = self.generate_otp()
            self.db_service.save_otp(user_id, otp, Config.OTP_EXPIRY_MINUTES)
            self.sns_service.send_otp_sms(phone_number, otp)
            
            # Generate voice prompt for OTP
            otp_prompt = self.polly_service.generate_otp_prompt()
            
            return {
                'success': True,
                'bill_id': bill_id,
                'bill_type': bill.get('bill_type'),
                'amount': bill.get('amount'),
                'due_date': bill.get('due_date'),
                'otp_prompt': otp_prompt,
                'message': f'OTP has been sent to your registered mobile number. {otp_prompt}'
            }
        except Exception as e:
            logger.error(f"Error initiating payment: {str(e)}")
            return {
                'success': False,
                'message': f'Error initiating payment: {str(e)}'
            }
    
    def verify_otp_and_pay(self, user_id: str, bill_id: str, otp: str) -> Dict[str, Any]:
        """
        Verify OTP and process payment.
        
        Args:
            user_id: User identifier
            bill_id: Bill identifier
            otp: OTP code to verify
            
        Returns:
            dict: Payment result
        """
        try:
            # Verify OTP
            if not self.db_service.verify_otp(user_id, otp):
                return {
                    'success': False,
                    'message': 'Invalid or expired OTP. Please try again.'
                }
            
            # Get bill details
            bill = self.db_service.get_bill_by_id(user_id, bill_id)
            if not bill:
                return {
                    'success': False,
                    'message': 'Bill not found'
                }
            
            # Process payment (mock payment gateway integration)
            payment_id = f"PAY-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{secrets.token_hex(4)}"
            payment = {
                'payment_id': payment_id,
                'user_id': user_id,
                'bill_id': bill_id,
                'amount': bill.get('amount'),
                'bill_type': bill.get('bill_type'),
                'payment_date': datetime.utcnow().isoformat(),
                'status': 'completed',
                'payment_method': 'voice_payment'
            }
            
            # Save payment record
            if self.db_service.create_payment(payment):
                # Generate confirmation message
                confirmation_text = self.polly_service.generate_payment_confirmation(payment)
                
                return {
                    'success': True,
                    'payment_id': payment_id,
                    'amount': payment['amount'],
                    'confirmation_message': confirmation_text,
                    'message': 'Payment processed successfully'
                }
            else:
                return {
                    'success': False,
                    'message': 'Error processing payment'
                }
        except Exception as e:
            logger.error(f"Error verifying OTP and paying: {str(e)}")
            return {
                'success': False,
                'message': f'Error processing payment: {str(e)}'
            }
    
    def get_user_bills_for_payment(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all unpaid bills for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            list: List of unpaid bills
        """
        try:
            bills = self.db_service.get_user_bills(user_id, include_paid=False)
            return bills
        except Exception as e:
            logger.error(f"Error getting user bills: {str(e)}")
            return []

