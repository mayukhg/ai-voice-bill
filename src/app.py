"""Main Flask application for AI Voice Bill Payment Service."""
import logging
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from src.config import Config
from src.services.reminder_service import ReminderService
from src.services.payment_service import PaymentService
from src.aws_services.lex_service import LexService
from src.utils.helpers import (
    validate_user_id,
    create_error_response,
    create_success_response,
    format_bill_response
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Initialize services
reminder_service = ReminderService()
payment_service = PaymentService()
lex_service = LexService()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'ai-voice-bill-payment'
    }), 200

@app.route('/api/v1/reminders/<user_id>', methods=['GET'])
def get_reminders(user_id: str):
    """
    Get bill reminders for a user (Flow 1).
    
    Returns list of due bills with reminder messages.
    """
    try:
        if not validate_user_id(user_id):
            return jsonify(create_error_response('Invalid user ID', 'INVALID_USER_ID')), 400
        
        reminders = reminder_service.get_all_reminders_for_user(user_id)
        
        return jsonify(create_success_response({
            'reminders': reminders,
            'count': len(reminders)
        }, f'Found {len(reminders)} bill reminders')), 200
    except Exception as e:
        logger.error(f"Error getting reminders: {str(e)}")
        return jsonify(create_error_response(str(e), 'REMINDER_ERROR')), 500

@app.route('/api/v1/reminders/<user_id>/audio/<bill_id>', methods=['GET'])
def get_reminder_audio(user_id: str, bill_id: str):
    """
    Get audio reminder for a specific bill.
    
    Returns MP3 audio stream.
    """
    try:
        from src.aws_services.dynamodb_service import DynamoDBService
        db_service = DynamoDBService()
        bill = db_service.get_bill_by_id(user_id, bill_id)
        
        if not bill:
            return jsonify(create_error_response('Bill not found', 'BILL_NOT_FOUND')), 404
        
        audio_data = reminder_service.generate_reminder_audio(bill)
        
        from flask import Response
        return Response(
            audio_data['audio_stream'],
            mimetype=audio_data['content_type'],
            headers={
                'Content-Disposition': f'attachment; filename=reminder_{bill_id}.mp3'
            }
        )
    except Exception as e:
        logger.error(f"Error generating reminder audio: {str(e)}")
        return jsonify(create_error_response(str(e), 'AUDIO_GENERATION_ERROR')), 500

@app.route('/api/v1/bills/<user_id>', methods=['GET'])
def get_user_bills(user_id: str):
    """Get all unpaid bills for a user."""
    try:
        if not validate_user_id(user_id):
            return jsonify(create_error_response('Invalid user ID', 'INVALID_USER_ID')), 400
        
        bills = payment_service.get_user_bills_for_payment(user_id)
        formatted_bills = [format_bill_response(bill) for bill in bills]
        
        return jsonify(create_success_response({
            'bills': formatted_bills,
            'count': len(formatted_bills)
        }, 'Bills retrieved successfully')), 200
    except Exception as e:
        logger.error(f"Error getting bills: {str(e)}")
        return jsonify(create_error_response(str(e), 'BILLS_ERROR')), 500

@app.route('/api/v1/payments/initiate', methods=['POST'])
def initiate_payment():
    """
    Initiate payment process (Flow 2 - Step 1).
    
    Request body:
    {
        "user_id": "user123",
        "bill_id": "bill456"
    }
    """
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        bill_id = data.get('bill_id')
        
        if not validate_user_id(user_id):
            return jsonify(create_error_response('Invalid user ID', 'INVALID_USER_ID')), 400
        
        if not bill_id:
            return jsonify(create_error_response('Bill ID is required', 'MISSING_BILL_ID')), 400
        
        result = payment_service.initiate_payment(user_id, bill_id)
        
        if result['success']:
            return jsonify(create_success_response(result, 'Payment initiated')), 200
        else:
            return jsonify(create_error_response(result['message'], 'PAYMENT_INIT_ERROR')), 400
    except Exception as e:
        logger.error(f"Error initiating payment: {str(e)}")
        return jsonify(create_error_response(str(e), 'PAYMENT_ERROR')), 500

@app.route('/api/v1/payments/verify', methods=['POST'])
def verify_otp_and_pay():
    """
    Verify OTP and process payment (Flow 2 - Step 2).
    
    Request body:
    {
        "user_id": "user123",
        "bill_id": "bill456",
        "otp": "123456"
    }
    """
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        bill_id = data.get('bill_id')
        otp = data.get('otp')
        
        if not validate_user_id(user_id):
            return jsonify(create_error_response('Invalid user ID', 'INVALID_USER_ID')), 400
        
        if not bill_id:
            return jsonify(create_error_response('Bill ID is required', 'MISSING_BILL_ID')), 400
        
        if not otp:
            return jsonify(create_error_response('OTP is required', 'MISSING_OTP')), 400
        
        result = payment_service.verify_otp_and_pay(user_id, bill_id, otp)
        
        if result['success']:
            return jsonify(create_success_response(result, 'Payment processed successfully')), 200
        else:
            return jsonify(create_error_response(result['message'], 'PAYMENT_VERIFICATION_ERROR')), 400
    except Exception as e:
        logger.error(f"Error verifying payment: {str(e)}")
        return jsonify(create_error_response(str(e), 'PAYMENT_ERROR')), 500

@app.route('/api/v1/lex/fulfillment', methods=['POST'])
def lex_fulfillment():
    """
    AWS Lex fulfillment endpoint.
    
    This endpoint handles Lex webhook calls for intent fulfillment.
    """
    try:
        lex_request = request.get_json()
        logger.info(f"Lex fulfillment request: {json.dumps(lex_request, indent=2)}")
        
        # Extract session attributes
        session_attributes = lex_request.get('sessionState', {}).get('sessionAttributes', {})
        user_id = session_attributes.get('user_id', 'default_user')
        
        # Extract intent
        intent = lex_request.get('sessionState', {}).get('intent', {})
        intent_name = intent.get('name')
        slots = intent.get('slots', {})
        
        # Handle different intents
        if intent_name == 'GetBillReminders':
            reminders = reminder_service.get_all_reminders_for_user(user_id)
            if reminders:
                message = f"You have {len(reminders)} bills due. "
                message += f"Your {reminders[0].get('bill_type')} bill of ${reminders[0].get('amount')} is due on {reminders[0].get('due_date')}. "
                message += "Would you like to pay it now?"
            else:
                message = "You have no bills due at this time."
            
            return jsonify({
                'sessionState': {
                    'dialogAction': {
                        'type': 'Close',
                        'fulfillmentState': 'Fulfilled'
                    },
                    'intent': {
                        'name': intent_name,
                        'state': 'Fulfilled'
                    }
                },
                'messages': [
                    {
                        'contentType': 'PlainText',
                        'content': message
                    }
                ]
            })
        
        elif intent_name == 'PayBill':
            bill_id = slots.get('BillId', {}).get('value', {}).get('interpretedValue')
            
            if not bill_id:
                # List available bills
                bills = payment_service.get_user_bills_for_payment(user_id)
                if bills:
                    message = f"You have {len(bills)} unpaid bills. "
                    message += "Please specify which bill you'd like to pay by saying the bill ID."
                else:
                    message = "You have no unpaid bills."
                
                return jsonify({
                    'sessionState': {
                        'dialogAction': {
                            'type': 'ElicitSlot',
                            'slotToElicit': 'BillId'
                        },
                        'intent': intent
                    },
                    'messages': [
                        {
                            'contentType': 'PlainText',
                            'content': message
                        }
                    ]
                })
            
            # Initiate payment
            result = payment_service.initiate_payment(user_id, bill_id)
            
            if result['success']:
                message = result['message']
            else:
                message = result['message']
            
            return jsonify({
                'sessionState': {
                    'dialogAction': {
                        'type': 'Close',
                        'fulfillmentState': 'Fulfilled' if result['success'] else 'Failed'
                    },
                    'intent': {
                        'name': intent_name,
                        'state': 'Fulfilled' if result['success'] else 'Failed'
                    }
                },
                'messages': [
                    {
                        'contentType': 'PlainText',
                        'content': message
                    }
                ]
            })
        
        elif intent_name == 'VerifyOTP':
            otp = slots.get('OTP', {}).get('value', {}).get('interpretedValue')
            bill_id = session_attributes.get('pending_bill_id')
            
            if not otp:
                return jsonify({
                    'sessionState': {
                        'dialogAction': {
                            'type': 'ElicitSlot',
                            'slotToElicit': 'OTP'
                        },
                        'intent': intent
                    },
                    'messages': [
                        {
                            'contentType': 'PlainText',
                            'content': 'Please provide the OTP sent to your mobile number.'
                        }
                    ]
                })
            
            if not bill_id:
                message = "No pending payment found. Please initiate a payment first."
            else:
                result = payment_service.verify_otp_and_pay(user_id, bill_id, otp)
                message = result.get('confirmation_message', result.get('message', 'Payment processed'))
            
            return jsonify({
                'sessionState': {
                    'dialogAction': {
                        'type': 'Close',
                        'fulfillmentState': 'Fulfilled'
                    },
                    'intent': {
                        'name': intent_name,
                        'state': 'Fulfilled'
                    }
                },
                'messages': [
                    {
                        'contentType': 'PlainText',
                        'content': message
                    }
                ]
            })
        
        else:
            return jsonify({
                'sessionState': {
                    'dialogAction': {
                        'type': 'Close',
                        'fulfillmentState': 'Failed'
                    }
                },
                'messages': [
                    {
                        'contentType': 'PlainText',
                        'content': "I didn't understand that. Could you please repeat?"
                    }
                ]
            })
    
    except Exception as e:
        logger.error(f"Error in Lex fulfillment: {str(e)}")
        return jsonify({
            'sessionState': {
                'dialogAction': {
                    'type': 'Close',
                    'fulfillmentState': 'Failed'
                }
            },
            'messages': [
                {
                    'contentType': 'PlainText',
                    'content': 'An error occurred. Please try again later.'
                }
            ]
        }), 500

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=Config.FLASK_DEBUG
    )

