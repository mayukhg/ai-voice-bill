"""Configuration management for the application."""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration."""
    
    # AWS Configuration
    AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    
    # Lex Bot Configuration
    LEX_BOT_NAME = os.getenv('LEX_BOT_NAME', 'BillPaymentBot')
    LEX_BOT_ALIAS = os.getenv('LEX_BOT_ALIAS', 'PROD')
    
    # Polly Configuration
    POLLY_VOICE_ID = os.getenv('POLLY_VOICE_ID', 'Joanna')
    POLLY_ENGINE = os.getenv('POLLY_ENGINE', 'neural')
    
    # DynamoDB Tables
    BILLS_TABLE = os.getenv('BILLS_TABLE', 'bills')
    USERS_TABLE = os.getenv('USERS_TABLE', 'users')
    PAYMENTS_TABLE = os.getenv('PAYMENTS_TABLE', 'payments')
    OTP_TABLE = os.getenv('OTP_TABLE', 'otp_records')
    
    # SNS Configuration
    SNS_TOPIC_ARN = os.getenv('SNS_TOPIC_ARN')
    
    # API Configuration
    API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:5000')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    # OTP Configuration
    OTP_EXPIRY_MINUTES = 5
    OTP_LENGTH = 6
    
    # OAuth 2.0 Configuration (for Alexa Account Linking)
    OAUTH_CLIENT_ID = os.getenv('OAUTH_CLIENT_ID', 'alexa_bill_payment_client')
    OAUTH_CLIENT_SECRET = os.getenv('OAUTH_CLIENT_SECRET', 'change_this_secret_in_production')
    OAUTH_REDIRECT_URI = os.getenv('OAUTH_REDIRECT_URI', 'https://pitangui.amazon.com/api/skill/link/YOUR_SKILL_ID')
    
    # Alexa Configuration
    ALEXA_CLIENT_ID = os.getenv('ALEXA_CLIENT_ID')  # LWA Client ID for Proactive Events
    ALEXA_CLIENT_SECRET = os.getenv('ALEXA_CLIENT_SECRET')  # LWA Client Secret
    ALEXA_SKILL_ID = os.getenv('ALEXA_SKILL_ID')
    
    # Lambda Configuration
    LAMBDA_FUNCTION_NAME = os.getenv('LAMBDA_FUNCTION_NAME', 'alexa-bill-payment-skill')
    LAMBDA_PROACTIVE_FUNCTION_NAME = os.getenv('LAMBDA_PROACTIVE_FUNCTION_NAME', 'alexa-bill-payment-proactive')

