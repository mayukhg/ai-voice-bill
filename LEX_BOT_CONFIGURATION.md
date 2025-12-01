# AWS Lex Bot Configuration Guide

This document provides instructions for configuring the AWS Lex bot for the AI Voice Bill Payment Service.

## Overview

The Lex bot handles natural language interactions for:
- **Flow 1**: Bill reminders
- **Flow 2**: Bill payments with OTP verification

## Bot Setup

### 1. Create Lex Bot

1. Go to AWS Lex Console
2. Click "Create bot"
3. Select "Create a blank bot"
4. Bot name: `BillPaymentBot`
5. Runtime role: Create a new IAM role with permissions for:
   - Lambda invocation
   - DynamoDB access
   - Polly access
   - SNS access

### 2. Intents Configuration

#### Intent 1: GetBillReminders

**Intent Name**: `GetBillReminders`

**Sample Utterances**:
- "What bills are due?"
- "Do I have any bills due?"
- "Show me my due bills"
- "Remind me about my bills"
- "What bills need to be paid?"

**Slots**: None required

**Fulfillment**:
- Use Lambda function: `lex-fulfillment-handler`
- Or use HTTP endpoint: `https://your-api-url/api/v1/lex/fulfillment`

#### Intent 2: PayBill

**Intent Name**: `PayBill`

**Sample Utterances**:
- "I want to pay my bill"
- "Pay my bills"
- "Pay bill {BillId}"
- "I'd like to make a payment"
- "Process payment for {BillId}"

**Slots**:
- `BillId` (Required)
  - Type: `AMAZON.AlphaNumeric`
  - Prompt: "Which bill would you like to pay? Please provide the bill ID."

**Fulfillment**:
- Use Lambda function or HTTP endpoint
- Saves `bill_id` in session attributes for OTP verification

#### Intent 3: VerifyOTP

**Intent Name**: `VerifyOTP`

**Sample Utterances**:
- "My OTP is {OTP}"
- "The code is {OTP}"
- "OTP {OTP}"
- "Verification code {OTP}"

**Slots**:
- `OTP` (Required)
  - Type: `AMAZON.Number`
  - Prompt: "Please provide the OTP sent to your mobile number."

**Fulfillment**:
- Retrieves `bill_id` from session attributes
- Verifies OTP and processes payment

### 3. Bot Alias Configuration

1. Create alias: `PROD`
2. Set version: Latest
3. Configure fulfillment:
   - Lambda function: `lex-fulfillment-handler`
   - Or HTTP endpoint: `https://your-api-url/api/v1/lex/fulfillment`

### 4. Session Attributes

The bot uses the following session attributes:
- `user_id`: User identifier (set during account linking)
- `pending_bill_id`: Bill ID for pending payment (set during PayBill intent)

### 5. Account Linking (Alexa Integration)

To enable Alexa account linking:

1. In Alexa Developer Console, configure OAuth 2.0:
   - Authorization URL: `https://your-api-url/oauth/authorize`
   - Access Token URL: `https://your-api-url/oauth/token`
   - Client ID and Secret

2. The `user_id` will be passed in session attributes after account linking.

## Lambda Function (Alternative to HTTP Endpoint)

If using Lambda instead of HTTP endpoint:

```python
import json
import boto3
import requests

def lambda_handler(event, context):
    # Forward to your API endpoint
    api_url = 'https://your-api-url/api/v1/lex/fulfillment'
    
    response = requests.post(api_url, json=event)
    return response.json()
```

## Testing

1. Use Lex Test Bot in AWS Console
2. Test each intent with sample utterances
3. Verify fulfillment responses
4. Test slot elicitation flow

## Deployment

1. Build the bot version
2. Create or update alias
3. Test with Alexa device or simulator
4. Monitor CloudWatch logs for errors

## Integration with Alexa

1. In Alexa Developer Console:
   - Create new skill
   - Enable "Alexa Conversations" or use "Custom" model
   - Configure Lex bot as backend
   - Enable account linking
   - Configure invocation name: "bill payment" or "my bills"

2. Test in Alexa Simulator or on physical device

## Best Practices

1. **Error Handling**: Always provide fallback responses
2. **Session Management**: Clear session attributes after payment completion
3. **Security**: Validate user_id in all fulfillment functions
4. **Logging**: Log all interactions for debugging
5. **Testing**: Test all conversation flows before production

## Sample Conversation Flow

**User**: "What bills are due?"
**Bot**: "You have 2 bills due. Your utility bill of $150.00 is due on 2024-01-15. Would you like to pay it now?"

**User**: "Yes, pay my utility bill"
**Bot**: "I've initiated payment for your utility bill. An OTP has been sent to your registered mobile number. Please provide the OTP."

**User**: "The code is 123456"
**Bot**: "Your payment of $150.00 for your utility bill has been successfully processed. A confirmation has been sent to your registered email and mobile number. Thank you for your payment!"

