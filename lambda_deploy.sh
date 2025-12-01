#!/bin/bash
# Deployment script for Alexa Skill Lambda function

set -e

echo "🚀 Deploying Alexa Skill Lambda Function..."

# Configuration
FUNCTION_NAME="alexa-bill-payment-skill"
REGION="us-east-1"
RUNTIME="python3.9"
HANDLER="src.alexa.lambda_function.lambda_handler"
ROLE_ARN="${LAMBDA_ROLE_ARN}"  # Set this environment variable

# Create deployment package
echo "📦 Creating deployment package..."
zip -r function.zip src/ requirements.txt -x "*.pyc" "__pycache__/*" "*.git*"

# Check if function exists
if aws lambda get-function --function-name $FUNCTION_NAME --region $REGION 2>/dev/null; then
    echo "📝 Updating existing function..."
    aws lambda update-function-code \
        --function-name $FUNCTION_NAME \
        --zip-file fileb://function.zip \
        --region $REGION
else
    echo "🆕 Creating new function..."
    aws lambda create-function \
        --function-name $FUNCTION_NAME \
        --runtime $RUNTIME \
        --role $ROLE_ARN \
        --handler $HANDLER \
        --zip-file fileb://function.zip \
        --timeout 30 \
        --memory-size 512 \
        --region $REGION \
        --environment Variables="{
            AWS_REGION=$AWS_REGION,
            BILLS_TABLE=$BILLS_TABLE,
            USERS_TABLE=$USERS_TABLE,
            PAYMENTS_TABLE=$PAYMENTS_TABLE,
            OTP_TABLE=$OTP_TABLE
        }"
fi

# Clean up
rm function.zip

echo "✅ Deployment complete!"
echo "📋 Function ARN:"
aws lambda get-function --function-name $FUNCTION_NAME --region $REGION --query 'Configuration.FunctionArn' --output text

