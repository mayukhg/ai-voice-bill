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

