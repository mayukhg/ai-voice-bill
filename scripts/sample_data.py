"""Script to populate sample data for testing."""
import boto3
import json
from datetime import datetime, timedelta
from decimal import Decimal
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.config import Config

def create_sample_data():
    """Create sample data in DynamoDB tables."""
    
    dynamodb = boto3.client(
        'dynamodb',
        region_name=Config.AWS_REGION,
        aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY
    )
    
    # Sample user
    user_id = "test_user_123"
    
    print("Creating sample user...")
    dynamodb.put_item(
        TableName=Config.USERS_TABLE,
        Item={
            'user_id': {'S': user_id},
            'email': {'S': 'test@example.com'},
            'phone_number': {'S': '+1234567890'},
            'name': {'S': 'Test User'},
            'created_at': {'S': datetime.utcnow().isoformat()}
        }
    )
    print(f"✓ Created user: {user_id}")
    
    # Sample bills
    bills = [
        {
            'bill_id': 'BILL-001',
            'bill_type': 'utility',
            'amount': 150.00,
            'due_date': (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d'),
            'description': 'Electricity bill for December',
            'is_paid': False
        },
        {
            'bill_id': 'BILL-002',
            'bill_type': 'credit_card',
            'amount': 500.00,
            'due_date': (datetime.now() + timedelta(days=10)).strftime('%Y-%m-%d'),
            'description': 'Credit card payment',
            'is_paid': False
        },
        {
            'bill_id': 'BILL-003',
            'bill_type': 'subscription',
            'amount': 29.99,
            'due_date': (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d'),
            'description': 'Monthly subscription service',
            'is_paid': False
        },
        {
            'bill_id': 'BILL-004',
            'bill_type': 'utility',
            'amount': 75.50,
            'due_date': (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d'),
            'description': 'Water bill for November',
            'is_paid': True
        }
    ]
    
    print("\nCreating sample bills...")
    for bill in bills:
        dynamodb.put_item(
            TableName=Config.BILLS_TABLE,
            Item={
                'user_id': {'S': user_id},
                'bill_id': {'S': bill['bill_id']},
                'bill_type': {'S': bill['bill_type']},
                'amount': {'N': str(bill['amount'])},
                'due_date': {'S': bill['due_date']},
                'description': {'S': bill['description']},
                'is_paid': {'BOOL': bill['is_paid']},
                'created_at': {'S': datetime.utcnow().isoformat()}
            }
        )
        print(f"✓ Created bill: {bill['bill_id']} - ${bill['amount']} due {bill['due_date']}")
    
    print("\n" + "="*50)
    print("Sample data created successfully!")
    print("="*50)
    print(f"\nUser ID: {user_id}")
    print("\nBills created:")
    for bill in bills:
        status = "PAID" if bill['is_paid'] else "UNPAID"
        print(f"  - {bill['bill_id']}: ${bill['amount']} ({bill['bill_type']}) - {status}")
    print("\nYou can now test the API with:")
    print(f"  curl http://localhost:5000/api/v1/reminders/{user_id}")
    print(f"  curl http://localhost:5000/api/v1/bills/{user_id}")

if __name__ == '__main__':
    try:
        create_sample_data()
    except Exception as e:
        print(f"Error creating sample data: {str(e)}")
        sys.exit(1)

