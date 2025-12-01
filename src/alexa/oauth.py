"""
OAuth 2.0 endpoints for Alexa account linking.
"""
import logging
import secrets
import hashlib
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, redirect, make_response
from src.config import Config
from src.aws_services.dynamodb_service import DynamoDBService
import base64

logger = logging.getLogger(__name__)

# OAuth configuration
CLIENT_ID = Config.OAUTH_CLIENT_ID if hasattr(Config, 'OAUTH_CLIENT_ID') else 'alexa_bill_payment_client'
CLIENT_SECRET = Config.OAUTH_CLIENT_SECRET if hasattr(Config, 'OAUTH_CLIENT_SECRET') else 'change_this_secret_in_production'
REDIRECT_URI = Config.OAUTH_REDIRECT_URI if hasattr(Config, 'OAUTH_REDIRECT_URI') else 'https://pitangui.amazon.com/api/skill/link/YOUR_SKILL_ID'

# In-memory storage for authorization codes (use DynamoDB in production)
authorization_codes = {}
access_tokens = {}

db_service = DynamoDBService()


def create_oauth_routes(app: Flask):
    """Register OAuth routes with Flask app."""
    
    @app.route('/oauth/authorize', methods=['GET'])
    def authorize():
        """
        OAuth 2.0 authorization endpoint.
        Returns authorization code.
        """
        try:
            # Get parameters
            client_id = request.args.get('client_id')
            response_type = request.args.get('response_type')
            redirect_uri = request.args.get('redirect_uri')
            state = request.args.get('state')
            scope = request.args.get('scope', '')
            
            logger.info(f"Authorization request: client_id={client_id}, response_type={response_type}")
            
            # Validate client_id
            if client_id != CLIENT_ID:
                return jsonify({'error': 'invalid_client'}), 400
            
            # Validate response_type
            if response_type != 'code':
                return jsonify({'error': 'unsupported_response_type'}), 400
            
            # Check if user is authenticated (in production, check session/auth)
            # For now, we'll require user_id as a parameter or use session
            user_id = request.args.get('user_id') or request.headers.get('X-User-Id')
            
            if not user_id:
                # In production, redirect to login page
                # For now, return error
                return jsonify({
                    'error': 'authentication_required',
                    'message': 'Please provide user_id'
                }), 401
            
            # Generate authorization code
            auth_code = secrets.token_urlsafe(32)
            authorization_codes[auth_code] = {
                'user_id': user_id,
                'client_id': client_id,
                'redirect_uri': redirect_uri,
                'scope': scope,
                'expires_at': datetime.utcnow() + timedelta(minutes=10)
            }
            
            # Build redirect URL with code
            redirect_url = f"{redirect_uri}?code={auth_code}"
            if state:
                redirect_url += f"&state={state}"
            
            logger.info(f"Authorization code generated: {auth_code[:8]}...")
            
            return redirect(redirect_url, code=302)
            
        except Exception as e:
            logger.error(f"Error in authorize: {str(e)}")
            return jsonify({'error': 'server_error'}), 500
    
    @app.route('/oauth/token', methods=['POST'])
    def token():
        """
        OAuth 2.0 token endpoint.
        Exchanges authorization code for access token.
        """
        try:
            # Get parameters
            grant_type = request.form.get('grant_type')
            code = request.form.get('code')
            redirect_uri = request.form.get('redirect_uri')
            
            # Get client credentials from Authorization header (HTTP Basic)
            auth_header = request.headers.get('Authorization', '')
            if auth_header.startswith('Basic '):
                encoded = auth_header[6:]
                decoded = base64.b64decode(encoded).decode('utf-8')
                client_id, client_secret = decoded.split(':', 1)
            else:
                client_id = request.form.get('client_id')
                client_secret = request.form.get('client_secret')
            
            logger.info(f"Token request: grant_type={grant_type}, client_id={client_id}")
            
            # Validate client credentials
            if client_id != CLIENT_ID or client_secret != CLIENT_SECRET:
                return jsonify({'error': 'invalid_client'}), 401
            
            # Validate grant_type
            if grant_type != 'authorization_code':
                return jsonify({'error': 'unsupported_grant_type'}), 400
            
            # Validate authorization code
            if code not in authorization_codes:
                return jsonify({'error': 'invalid_grant'}), 400
            
            auth_data = authorization_codes[code]
            
            # Check expiration
            if datetime.utcnow() > auth_data['expires_at']:
                del authorization_codes[code]
                return jsonify({'error': 'invalid_grant', 'error_description': 'Authorization code expired'}), 400
            
            # Validate redirect_uri
            if redirect_uri != auth_data['redirect_uri']:
                return jsonify({'error': 'invalid_grant'}), 400
            
            # Generate access token
            access_token = secrets.token_urlsafe(64)
            refresh_token = secrets.token_urlsafe(64)
            
            # Store access token
            access_tokens[access_token] = {
                'user_id': auth_data['user_id'],
                'client_id': client_id,
                'scope': auth_data['scope'],
                'expires_at': datetime.utcnow() + timedelta(hours=1),
                'refresh_token': refresh_token
            }
            
            # Clean up authorization code
            del authorization_codes[code]
            
            logger.info(f"Access token generated for user: {auth_data['user_id']}")
            
            # Return token response
            return jsonify({
                'access_token': access_token,
                'token_type': 'Bearer',
                'expires_in': 3600,
                'refresh_token': refresh_token,
                'scope': auth_data['scope']
            }), 200
            
        except Exception as e:
            logger.error(f"Error in token: {str(e)}")
            return jsonify({'error': 'server_error'}), 500
    
    @app.route('/oauth/refresh', methods=['POST'])
    def refresh_token():
        """
        OAuth 2.0 token refresh endpoint.
        """
        try:
            refresh_token = request.form.get('refresh_token')
            client_id = request.form.get('client_id')
            client_secret = request.form.get('client_secret')
            
            # Find token by refresh_token
            token_data = None
            for token, data in access_tokens.items():
                if data.get('refresh_token') == refresh_token:
                    token_data = data
                    break
            
            if not token_data:
                return jsonify({'error': 'invalid_grant'}), 400
            
            # Validate client
            if client_id != CLIENT_ID or client_secret != CLIENT_SECRET:
                return jsonify({'error': 'invalid_client'}), 401
            
            # Generate new access token
            new_access_token = secrets.token_urlsafe(64)
            new_refresh_token = secrets.token_urlsafe(64)
            
            # Update token
            access_tokens[new_access_token] = {
                'user_id': token_data['user_id'],
                'client_id': client_id,
                'scope': token_data['scope'],
                'expires_at': datetime.utcnow() + timedelta(hours=1),
                'refresh_token': new_refresh_token
            }
            
            # Remove old token
            for token in list(access_tokens.keys()):
                if access_tokens[token].get('refresh_token') == refresh_token:
                    del access_tokens[token]
                    break
            
            return jsonify({
                'access_token': new_access_token,
                'token_type': 'Bearer',
                'expires_in': 3600,
                'refresh_token': new_refresh_token
            }), 200
            
        except Exception as e:
            logger.error(f"Error in refresh_token: {str(e)}")
            return jsonify({'error': 'server_error'}), 500
    
    @app.route('/oauth/userinfo', methods=['GET'])
    def userinfo():
        """
        Get user information from access token.
        """
        try:
            # Get access token from Authorization header
            auth_header = request.headers.get('Authorization', '')
            if not auth_header.startswith('Bearer '):
                return jsonify({'error': 'invalid_token'}), 401
            
            access_token = auth_header[7:]
            
            if access_token not in access_tokens:
                return jsonify({'error': 'invalid_token'}), 401
            
            token_data = access_tokens[access_token]
            
            # Check expiration
            if datetime.utcnow() > token_data['expires_at']:
                return jsonify({'error': 'invalid_token', 'error_description': 'Token expired'}), 401
            
            # Get user info
            user_id = token_data['user_id']
            user = db_service.get_user(user_id)
            
            if not user:
                return jsonify({'error': 'user_not_found'}), 404
            
            return jsonify({
                'user_id': user_id,
                'email': user.get('email'),
                'name': user.get('name'),
                'phone_number': user.get('phone_number')
            }), 200
            
        except Exception as e:
            logger.error(f"Error in userinfo: {str(e)}")
            return jsonify({'error': 'server_error'}), 500
    
    @app.route('/oauth/validate', methods=['POST'])
    def validate_token():
        """
        Validate access token (used by Alexa).
        """
        try:
            access_token = request.json.get('access_token')
            
            if not access_token or access_token not in access_tokens:
                return jsonify({'valid': False}), 200
            
            token_data = access_tokens[access_token]
            
            # Check expiration
            if datetime.utcnow() > token_data['expires_at']:
                return jsonify({'valid': False}), 200
            
            return jsonify({
                'valid': True,
                'user_id': token_data['user_id'],
                'scope': token_data['scope']
            }), 200
            
        except Exception as e:
            logger.error(f"Error in validate_token: {str(e)}")
            return jsonify({'valid': False}), 200

