# Quick Start Guide

Get up and running with the AI Voice Bill Payment Service in 5 minutes.

## Prerequisites Check

- [ ] Python 3.9+ installed (`python --version`)
- [ ] AWS Account with credentials
- [ ] AWS CLI configured (optional)

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and add your AWS credentials:
```bash
AWS_ACCESS_KEY_ID=your_key_here
AWS_SECRET_ACCESS_KEY=your_secret_here
AWS_REGION=us-east-1
```

## Step 3: Create DynamoDB Tables (Quick Setup)

Run these AWS CLI commands (or use AWS Console):

```bash
# Set your region
export AWS_DEFAULT_REGION=us-east-1

# Create bills table
aws dynamodb create-table \
  --table-name bills \
  --attribute-definitions AttributeName=user_id,AttributeType=S AttributeName=bill_id,AttributeType=S \
  --key-schema AttributeName=user_id,KeyType=HASH AttributeName=bill_id,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST

# Create users table
aws dynamodb create-table \
  --table-name users \
  --attribute-definitions AttributeName=user_id,AttributeType=S \
  --key-schema AttributeName=user_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST

# Create payments table
aws dynamodb create-table \
  --table-name payments \
  --attribute-definitions AttributeName=payment_id,AttributeType=S \
  --key-schema AttributeName=payment_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST

# Create OTP table
aws dynamodb create-table \
  --table-name otp_records \
  --attribute-definitions AttributeName=user_id,AttributeType=S AttributeName=otp,AttributeType=S \
  --key-schema AttributeName=user_id,KeyType=HASH AttributeName=otp,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST
```

## Step 4: Add Sample Data

```bash
python scripts/sample_data.py
```

This creates:
- A test user (`test_user_123`)
- Sample bills (some due, some paid)

## Step 5: Start the Server

```bash
python src/app.py
```

You should see:
```
 * Running on http://0.0.0.0:5000
```

## Step 6: Test the API

### Health Check
```bash
curl http://localhost:5000/health
```

### Get Reminders
```bash
curl http://localhost:5000/api/v1/reminders/test_user_123
```

### Get Bills
```bash
curl http://localhost:5000/api/v1/bills/test_user_123
```

### Test Payment Flow

**1. Initiate Payment:**
```bash
curl -X POST http://localhost:5000/api/v1/payments/initiate \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test_user_123", "bill_id": "BILL-001"}'
```

**2. Check logs for OTP** (in development mode, OTP is logged)

**3. Verify OTP and Pay:**
```bash
curl -X POST http://localhost:5000/api/v1/payments/verify \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test_user_123", "bill_id": "BILL-001", "otp": "123456"}'
```

## Next Steps

1. **Set up AWS Lex Bot**: See [LEX_BOT_CONFIGURATION.md](LEX_BOT_CONFIGURATION.md)
2. **Configure AWS Polly**: Already configured in code (uses "Joanna" voice)
3. **Set up SNS for OTP**: Configure SNS topic in `.env` (optional for testing)
4. **Deploy to Production**: See [DEPLOYMENT.md](DEPLOYMENT.md)

## Troubleshooting

### Import Errors
```bash
# Make sure you're in the project root
cd /path/to/ai-voice-bill
# Install dependencies
pip install -r requirements.txt
```

### AWS Credential Errors
- Check `.env` file has correct credentials
- Verify AWS credentials have necessary permissions
- Test with: `aws sts get-caller-identity`

### DynamoDB Errors
- Verify tables are created
- Check table names match `.env` configuration
- Ensure AWS region is correct

### Port Already in Use
```bash
# Use a different port
export FLASK_RUN_PORT=5001
python src/app.py
```

## Development Tips

1. **Enable Debug Mode**: Set `FLASK_DEBUG=True` in `.env`
2. **View Logs**: Check console output for detailed logs
3. **Test Locally First**: Always test API endpoints before Lex integration
4. **Use Sample Data**: The sample data script helps with quick testing

## Need Help?

- Check [README.md](README.md) for overview
- See [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for API details
- Review [ARCHITECTURE.md](ARCHITECTURE.md) for system design

