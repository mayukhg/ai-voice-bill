"""DynamoDB service for data storage."""
import boto3
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from decimal import Decimal
from src.config import Config

logger = logging.getLogger(__name__)

class DynamoDBService:
    """Service for interacting with DynamoDB."""
    
    def __init__(self):
        """Initialize DynamoDB client."""
        self.client = boto3.client(
            'dynamodb',
            region_name=Config.AWS_REGION,
            aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY
        )
        self.bills_table = Config.BILLS_TABLE
        self.users_table = Config.USERS_TABLE
        self.payments_table = Config.PAYMENTS_TABLE
        self.otp_table = Config.OTP_TABLE
    
    def get_user_bills(self, user_id: str, include_paid: bool = False) -> List[Dict[str, Any]]:
        """
        Get all bills for a user.
        
        Args:
            user_id: User identifier
            include_paid: Whether to include paid bills
            
        Returns:
            list: List of bill dictionaries
        """
        try:
            response = self.client.query(
                TableName=self.bills_table,
                KeyConditionExpression='user_id = :uid',
                ExpressionAttributeValues={
                    ':uid': {'S': user_id},
                    ':paid': {'BOOL': include_paid}
                },
                FilterExpression='is_paid = :paid' if not include_paid else None
            )
            
            bills = []
            for item in response.get('Items', []):
                bills.append(self._unmarshal_item(item))
            
            return bills
        except Exception as e:
            logger.error(f"Error getting user bills: {str(e)}")
            return []
    
    def get_due_bills(self, user_id: str, days_ahead: int = 7) -> List[Dict[str, Any]]:
        """
        Get bills that are due within specified days.
        
        Args:
            user_id: User identifier
            days_ahead: Number of days to look ahead
            
        Returns:
            list: List of due bills
        """
        try:
            all_bills = self.get_user_bills(user_id, include_paid=False)
            today = datetime.now().date()
            cutoff_date = today + timedelta(days=days_ahead)
            
            due_bills = []
            for bill in all_bills:
                due_date_str = bill.get('due_date')
                if due_date_str:
                    due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
                    if today <= due_date <= cutoff_date:
                        due_bills.append(bill)
            
            return due_bills
        except Exception as e:
            logger.error(f"Error getting due bills: {str(e)}")
            return []
    
    def get_bill_by_id(self, user_id: str, bill_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific bill by ID.
        
        Args:
            user_id: User identifier
            bill_id: Bill identifier
            
        Returns:
            dict: Bill dictionary or None
        """
        try:
            response = self.client.get_item(
                TableName=self.bills_table,
                Key={
                    'user_id': {'S': user_id},
                    'bill_id': {'S': bill_id}
                }
            )
            
            if 'Item' in response:
                return self._unmarshal_item(response['Item'])
            return None
        except Exception as e:
            logger.error(f"Error getting bill: {str(e)}")
            return None
    
    def create_payment(self, payment: Dict[str, Any]) -> bool:
        """
        Create a payment record.
        
        Args:
            payment: Payment dictionary
            
        Returns:
            bool: True if successful
        """
        try:
            item = self._marshal_item(payment)
            self.client.put_item(
                TableName=self.payments_table,
                Item=item
            )
            
            # Mark bill as paid
            self._update_bill_status(payment['user_id'], payment['bill_id'], True)
            
            logger.info(f"Payment created: {payment.get('payment_id')}")
            return True
        except Exception as e:
            logger.error(f"Error creating payment: {str(e)}")
            return False
    
    def _update_bill_status(self, user_id: str, bill_id: str, is_paid: bool):
        """Update bill payment status."""
        try:
            self.client.update_item(
                TableName=self.bills_table,
                Key={
                    'user_id': {'S': user_id},
                    'bill_id': {'S': bill_id}
                },
                UpdateExpression='SET is_paid = :paid',
                ExpressionAttributeValues={
                    ':paid': {'BOOL': is_paid}
                }
            )
        except Exception as e:
            logger.error(f"Error updating bill status: {str(e)}")
    
    def save_otp(self, user_id: str, otp: str, expiry_minutes: int = 5) -> bool:
        """
        Save OTP record.
        
        Args:
            user_id: User identifier
            otp: OTP code
            expiry_minutes: OTP expiry time in minutes
            
        Returns:
            bool: True if successful
        """
        try:
            expiry_time = datetime.utcnow() + timedelta(minutes=expiry_minutes)
            item = {
                'user_id': {'S': user_id},
                'otp': {'S': otp},
                'expiry_time': {'S': expiry_time.isoformat()},
                'is_used': {'BOOL': False},
                'created_at': {'S': datetime.utcnow().isoformat()}
            }
            
            self.client.put_item(
                TableName=self.otp_table,
                Item=item
            )
            
            return True
        except Exception as e:
            logger.error(f"Error saving OTP: {str(e)}")
            return False
    
    def verify_otp(self, user_id: str, otp: str) -> bool:
        """
        Verify OTP code.
        
        Args:
            user_id: User identifier
            otp: OTP code to verify
            
        Returns:
            bool: True if OTP is valid
        """
        try:
            response = self.client.get_item(
                TableName=self.otp_table,
                Key={
                    'user_id': {'S': user_id},
                    'otp': {'S': otp}
                }
            )
            
            if 'Item' not in response:
                return False
            
            item = self._unmarshal_item(response['Item'])
            
            # Check if already used
            if item.get('is_used', False):
                return False
            
            # Check expiry
            expiry_time = datetime.fromisoformat(item['expiry_time'])
            if datetime.utcnow() > expiry_time:
                return False
            
            # Mark as used
            self.client.update_item(
                TableName=self.otp_table,
                Key={
                    'user_id': {'S': user_id},
                    'otp': {'S': otp}
                },
                UpdateExpression='SET is_used = :used',
                ExpressionAttributeValues={
                    ':used': {'BOOL': True}
                }
            )
            
            return True
        except Exception as e:
            logger.error(f"Error verifying OTP: {str(e)}")
            return False
    
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user information."""
        try:
            response = self.client.get_item(
                TableName=self.users_table,
                Key={'user_id': {'S': user_id}}
            )
            
            if 'Item' in response:
                return self._unmarshal_item(response['Item'])
            return None
        except Exception as e:
            logger.error(f"Error getting user: {str(e)}")
            return None
    
    def _marshal_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Python dict to DynamoDB format."""
        marshalled = {}
        for key, value in item.items():
            if isinstance(value, str):
                marshalled[key] = {'S': value}
            elif isinstance(value, (int, float)):
                marshalled[key] = {'N': str(value)}
            elif isinstance(value, bool):
                marshalled[key] = {'BOOL': value}
            elif isinstance(value, dict):
                marshalled[key] = {'M': self._marshal_item(value)}
            elif isinstance(value, list):
                marshalled[key] = {'L': [self._marshal_item(v) if isinstance(v, dict) else {'S': str(v)} for v in value]}
        return marshalled
    
    def _unmarshal_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Convert DynamoDB format to Python dict."""
        unmarshalled = {}
        for key, value in item.items():
            if 'S' in value:
                unmarshalled[key] = value['S']
            elif 'N' in value:
                unmarshalled[key] = float(value['N']) if '.' in value['N'] else int(value['N'])
            elif 'BOOL' in value:
                unmarshalled[key] = value['BOOL']
            elif 'M' in value:
                unmarshalled[key] = self._unmarshal_item(value['M'])
            elif 'L' in value:
                unmarshalled[key] = [self._unmarshal_item(v) if 'M' in v else v.get('S', '') for v in value['L']]
        return unmarshalled

