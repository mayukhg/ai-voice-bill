# Deployment Guide

This guide covers deployment of the AI Voice Bill Payment Service to various environments.

## Prerequisites

- AWS Account with appropriate IAM permissions
- AWS CLI installed and configured
- Python 3.9+ installed
- Docker (optional, for containerized deployment)

## AWS Resources Setup

### 1. DynamoDB Tables

Create the following tables using AWS Console or CLI:

```bash
# Create bills table
aws dynamodb create-table \
  --table-name bills \
  --attribute-definitions \
    AttributeName=user_id,AttributeType=S \
    AttributeName=bill_id,AttributeType=S \
  --key-schema \
    AttributeName=user_id,KeyType=HASH \
    AttributeName=bill_id,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST

# Create users table
aws dynamodb create-table \
  --table-name users \
  --attribute-definitions \
    AttributeName=user_id,AttributeType=S \
  --key-schema \
    AttributeName=user_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST

# Create payments table
aws dynamodb create-table \
  --table-name payments \
  --attribute-definitions \
    AttributeName=payment_id,AttributeType=S \
  --key-schema \
    AttributeName=payment_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST

# Create OTP records table
aws dynamodb create-table \
  --table-name otp_records \
  --attribute-definitions \
    AttributeName=user_id,AttributeType=S \
    AttributeName=otp,AttributeType=S \
  --key-schema \
    AttributeName=user_id,KeyType=HASH \
    AttributeName=otp,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST
```

### 2. IAM Role for Lambda (if using Lambda)

Create IAM role with policies:
- `AmazonDynamoDBFullAccess` (or scoped permissions)
- `AmazonPollyFullAccess`
- `AmazonLexFullAccess`
- `AmazonSNSFullAccess`
- `AWSLambdaBasicExecutionRole`

### 3. SNS Topic (Optional)

```bash
aws sns create-topic --name otp-notifications
```

Note the Topic ARN and add to `.env` file.

### 4. AWS Lex Bot

Follow [LEX_BOT_CONFIGURATION.md](LEX_BOT_CONFIGURATION.md) to create and configure the Lex bot.

## Local Development Deployment

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your AWS credentials
```

### 3. Run Application

```bash
python src/app.py
```

Application runs on `http://localhost:5000`

## AWS Lambda Deployment

### Option 1: Using AWS SAM

1. Create `template.yaml`:

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Resources:
  VoiceBillAPI:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: src/
      Handler: app.lambda_handler
      Runtime: python3.9
      Environment:
        Variables:
          AWS_REGION: us-east-1
      Events:
        Api:
          Type: Api
          Properties:
            Path: /{proxy+}
            Method: ANY
```

2. Build and deploy:

```bash
sam build
sam deploy --guided
```

### Option 2: Manual Lambda Deployment

1. Package application:

```bash
zip -r function.zip src/ requirements.txt
```

2. Create Lambda function:
   - Runtime: Python 3.9
   - Handler: `app.lambda_handler`
   - Upload `function.zip`

3. Configure environment variables in Lambda console

4. Create API Gateway:
   - Create REST API
   - Create resource: `/{proxy+}`
   - Create method: `ANY`
   - Integration type: Lambda Function
   - Select your Lambda function

### Lambda Handler Wrapper

Add to `src/app.py`:

```python
def lambda_handler(event, context):
    """Lambda handler wrapper for AWS Lambda."""
    from awsgi import response
    
    return response(app, event, context)
```

Install `awsgi`:
```bash
pip install awsgi
```

## Docker Deployment

### 1. Create Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

EXPOSE 5000

CMD ["python", "src/app.py"]
```

### 2. Build and Run

```bash
docker build -t ai-voice-bill .
docker run -p 5000:5000 --env-file .env ai-voice-bill
```

### 3. Deploy to ECS/Fargate

1. Push image to ECR
2. Create ECS task definition
3. Create ECS service
4. Configure load balancer

## Environment Variables

Required environment variables:

```bash
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
LEX_BOT_NAME=BillPaymentBot
LEX_BOT_ALIAS=PROD
POLLY_VOICE_ID=Joanna
POLLY_ENGINE=neural
BILLS_TABLE=bills
USERS_TABLE=users
PAYMENTS_TABLE=payments
OTP_TABLE=otp_records
SNS_TOPIC_ARN=arn:aws:sns:us-east-1:123456789012:otp-notifications
FLASK_ENV=production
FLASK_DEBUG=False
```

## Testing Deployment

### 1. Health Check

```bash
curl https://your-api-url/health
```

### 2. Test Reminders

```bash
curl https://your-api-url/api/v1/reminders/test_user
```

### 3. Test Payment Flow

```bash
# Initiate payment
curl -X POST https://your-api-url/api/v1/payments/initiate \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test_user", "bill_id": "test_bill"}'

# Verify OTP (use OTP from logs/SMS)
curl -X POST https://your-api-url/api/v1/payments/verify \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test_user", "bill_id": "test_bill", "otp": "123456"}'
```

## Monitoring

### CloudWatch Logs

- Lambda logs: `/aws/lambda/your-function-name`
- API Gateway logs: Enable in API Gateway console

### CloudWatch Metrics

Monitor:
- API request count
- API latency
- Error rates
- DynamoDB read/write capacity

### Alarms

Set up CloudWatch alarms for:
- High error rates (> 5%)
- High latency (> 2 seconds)
- DynamoDB throttling

## Security Best Practices

1. **Secrets Management**: Use AWS Secrets Manager or Parameter Store for credentials
2. **VPC**: Deploy Lambda in VPC if accessing private resources
3. **IAM Roles**: Use IAM roles instead of access keys when possible
4. **HTTPS Only**: Enforce HTTPS in API Gateway
5. **Rate Limiting**: Configure API Gateway throttling
6. **CORS**: Configure CORS appropriately
7. **Encryption**: Enable encryption at rest for DynamoDB

## Scaling

### Auto-Scaling

- **Lambda**: Automatically scales based on requests
- **API Gateway**: Handles up to 10,000 requests/second
- **DynamoDB**: Auto-scales with on-demand billing

### Performance Tuning

1. Enable DynamoDB auto-scaling
2. Use connection pooling for external services
3. Implement caching where appropriate
4. Optimize Lambda memory allocation

## Rollback Procedure

1. Keep previous Lambda version
2. Update API Gateway to point to previous version
3. Monitor for issues
4. Fix issues in new version
5. Re-deploy when ready

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are in `requirements.txt`
2. **Permission Errors**: Check IAM roles and policies
3. **Timeout Errors**: Increase Lambda timeout
4. **Cold Starts**: Use provisioned concurrency for critical functions

### Debugging

1. Check CloudWatch Logs
2. Enable detailed logging
3. Test locally first
4. Use AWS X-Ray for tracing

## Production Checklist

- [ ] All environment variables configured
- [ ] DynamoDB tables created
- [ ] IAM roles and policies set up
- [ ] Lex bot configured and tested
- [ ] API Gateway configured
- [ ] CloudWatch alarms set up
- [ ] Security groups configured
- [ ] HTTPS enabled
- [ ] Rate limiting configured
- [ ] Monitoring and logging enabled
- [ ] Backup strategy in place
- [ ] Documentation updated

