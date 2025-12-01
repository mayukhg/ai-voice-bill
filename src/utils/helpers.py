"""Helper utility functions."""
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

def validate_user_id(user_id: Optional[str]) -> bool:
    """
    Validate user ID format.
    
    Args:
        user_id: User identifier to validate
        
    Returns:
        bool: True if valid
    """
    if not user_id or not isinstance(user_id, str):
        return False
    return len(user_id.strip()) > 0

def format_bill_response(bill: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format bill dictionary for API response.
    
    Args:
        bill: Bill dictionary
        
    Returns:
        dict: Formatted bill dictionary
    """
    return {
        'bill_id': bill.get('bill_id'),
        'bill_type': bill.get('bill_type'),
        'amount': float(bill.get('amount', 0)),
        'due_date': bill.get('due_date'),
        'is_paid': bill.get('is_paid', False),
        'description': bill.get('description', '')
    }

def format_payment_response(payment: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format payment dictionary for API response.
    
    Args:
        payment: Payment dictionary
        
    Returns:
        dict: Formatted payment dictionary
    """
    return {
        'payment_id': payment.get('payment_id'),
        'bill_id': payment.get('bill_id'),
        'amount': float(payment.get('amount', 0)),
        'status': payment.get('status'),
        'payment_date': payment.get('payment_date'),
        'payment_method': payment.get('payment_method')
    }

def create_error_response(message: str, error_code: str = 'GENERAL_ERROR') -> Dict[str, Any]:
    """
    Create standardized error response.
    
    Args:
        message: Error message
        error_code: Error code
        
    Returns:
        dict: Error response dictionary
    """
    return {
        'success': False,
        'error': {
            'code': error_code,
            'message': message,
            'timestamp': datetime.utcnow().isoformat()
        }
    }

def create_success_response(data: Dict[str, Any], message: str = 'Success') -> Dict[str, Any]:
    """
    Create standardized success response.
    
    Args:
        data: Response data
        message: Success message
        
    Returns:
        dict: Success response dictionary
    """
    return {
        'success': True,
        'message': message,
        'data': data,
        'timestamp': datetime.utcnow().isoformat()
    }

