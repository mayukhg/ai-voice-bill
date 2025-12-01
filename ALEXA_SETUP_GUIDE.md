# Alexa Skill Setup Guide

Complete guide for setting up and configuring the Bill Payment Assistant Alexa Skill.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Initial Setup](#initial-setup)
3. [AWS Configuration](#aws-configuration)
4. [Alexa Developer Console Setup](#alexa-developer-console-setup)
5. [Account Linking Configuration](#account-linking-configuration)
6. [Testing](#testing)
7. [Deployment](#deployment)

## Prerequisites

### Required Accounts

1. **Amazon Developer Account**
   - Sign up at https://developer.amazon.com
   - Complete account verification
   - Enable 2FA for security

2. **AWS Account**
   - Create AWS account if you don't have one
   - Set up IAM user with appropriate permissions
   - Configure AWS CLI

3. **Domain Name** (for hosting privacy policy and terms)
   - Register domain or use existing
   - Set up SSL certificate (HTTPS required)

### Required Software

- Python 3.9 or higher
- Node.js 14+ (for ASK CLI)
- AWS CLI
- Git

## Initial Setup

### 1. Install ASK CLI

```bash
npm install -g ask-cli
ask configure
```

Follow the prompts to authenticate with your Amazon Developer account.

### 2. Clone and Setup Project

```bash
git clone https://github.com/mayukhg/ai-voice-bill.git
cd ai-voice-bill
git checkout alexa-app
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
cp .env.example .env
# Edit .env with your configuration
```

## AWS Configuration

### 1. Create DynamoDB Tables

Run the following AWS CLI commands or use AWS Console:

```bash
# Bills table
aws dynamodb create-table \
  --table-name bills \
  --attribute-definitions \
    AttributeName=user_id,AttributeType=S \
    AttributeName=bill_id,AttributeType=S \
  --key-schema \
    AttributeName=user_id,KeyType=HASH \
    AttributeName=bill_id,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1

# Users table
aws dynamodb create-table \
  --table-name users \
  --attribute-definitions \
    AttributeName=user_id,AttributeType=S \
  --key-schema \
    AttributeName=user_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1

# Payments table
aws dynamodb create-table \
  --table-name payments \
  --attribute-definitions \
    AttributeName=payment_id,AttributeType=S \
  --key-schema \
    AttributeName=payment_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1

# OTP records table
aws dynamodb create-table \
  --table-name otp_records \
  --attribute-definitions \
    AttributeName=user_id,AttributeType=S \
    AttributeName=otp,AttributeType=S \
  --key-schema \
    AttributeName=user_id,KeyType=HASH \
    AttributeName=otp,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1
```

### 2. Create IAM Role for Lambda

```bash
# Create trust policy
cat > trust-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

# Create role
aws iam create-role \
  --role-name lambda-execution-role \
  --assume-role-policy-document file://trust-policy.json

# Attach policies
aws iam attach-role-policy \
  --role-name lambda-execution-role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

# Create and attach custom policy for DynamoDB, SNS, Polly
# (See ALEXA_DEPLOYMENT.md for policy JSON)
```

### 3. Create SNS Topic (for OTP)

```bash
aws sns create-topic --name otp-notifications --region us-east-1
```

## Alexa Developer Console Setup

### 1. Create New Skill

1. Go to https://developer.amazon.com/alexa/console/ask
2. Click "Create Skill"
3. Choose "Custom" model
4. Select "Provision your own" for backend
5. Name: "Bill Payment Assistant"
6. Click "Create skill"

### 2. Upload Skill Manifest

1. Go to "JSON Editor" in left sidebar
2. Copy contents of `skill.json`
3. Replace placeholders:
   - `ACCOUNT_ID` with your AWS account ID
   - `YOUR_SKILL_ID` with your skill ID
   - Update Lambda ARN
   - Update icon URLs
4. Click "Save Model"

### 3. Upload Interaction Model

1. Go to "Interaction Model" → "JSON Editor"
2. Copy contents of `src/alexa/interaction_model.json`
3. Click "Save Model"
4. Click "Build Model"

### 4. Configure Account Linking

1. Go to "Account Linking"
2. Enable "Account Linking"
3. Select "Auth Code Grant"
4. Configure:
   - **Authorization URI**: `https://your-domain.com/oauth/authorize`
   - **Access Token URI**: `https://your-domain.com/oauth/token`
   - **Client ID**: Your OAuth client ID
   - **Client Secret**: Your OAuth client secret
   - **Client Authentication Scheme**: HTTP Basic
   - **Scopes**: `profile`, `bills`, `payments`
   - **Domain List**: `your-domain.com`
5. Add redirect URIs (provided by Amazon)
6. Click "Save"

### 5. Configure Privacy and Compliance

1. Go to "Privacy & Compliance"
2. Upload privacy policy URL: `https://your-domain.com/privacy-policy`
3. Upload terms of use URL: `https://your-domain.com/terms-of-service`
4. Configure:
   - Allows Purchases: No
   - Uses Personal Info: Yes
   - Contains Ads: No
   - Is Child Directed: No
   - Is Export Compliant: Yes
5. Click "Save"

### 6. Configure Publishing Information

1. Go to "Distribution"
2. Fill in:
   - **Skill Name**: Bill Payment Assistant
   - **Invocation Name**: bill payment
   - **Category**: Finance
   - **Short Description**: (from skill.json)
   - **Full Description**: (from skill.json)
   - **Example Phrases**: (from skill.json)
   - **Keywords**: (from skill.json)
3. Upload icons:
   - Small icon: 108x108px
   - Large icon: 512x512px
   - Preview image: 1200x800px
4. Click "Save"

## Account Linking Configuration

### 1. Deploy OAuth Endpoints

Deploy your Flask application with OAuth routes:

```bash
# Deploy to AWS Elastic Beanstalk, EC2, or Lambda + API Gateway
# Ensure HTTPS is enabled
```

### 2. Test OAuth Flow

1. Test authorization endpoint:
   ```bash
   curl "https://your-domain.com/oauth/authorize?client_id=test&response_type=code&redirect_uri=https://pitangui.amazon.com/api/skill/link/YOUR_SKILL_ID"
   ```

2. Test token endpoint:
   ```bash
   curl -X POST https://your-domain.com/oauth/token \
     -H "Authorization: Basic base64(client_id:client_secret)" \
     -d "grant_type=authorization_code&code=AUTH_CODE&redirect_uri=REDIRECT_URI"
   ```

## Testing

### 1. Test in Developer Console

1. Go to "Test" tab in Developer Console
2. Enable testing for your account
3. Type or say: "open bill payment"
4. Test all intents

### 2. Test on Device

1. Enable skill in Alexa app
2. Link account
3. Say: "Alexa, open bill payment"
4. Test all features

### 3. Test Account Linking

1. Open Alexa app
2. Go to Skills → Your Skills
3. Find "Bill Payment Assistant"
4. Click "Enable"
5. Complete account linking
6. Test skill

## Deployment

### 1. Deploy Lambda Function

```bash
chmod +x lambda_deploy.sh
export LAMBDA_ROLE_ARN="arn:aws:iam::ACCOUNT_ID:role/lambda-execution-role"
./lambda_deploy.sh
```

### 2. Update Skill Manifest

Update `skill.json` with Lambda ARN:
```json
"uri": "arn:aws:lambda:us-east-1:ACCOUNT_ID:function:alexa-bill-payment-skill"
```

### 3. Deploy Skill

```bash
ask deploy
```

Or manually:
1. Copy updated `skill.json` to Developer Console
2. Click "Save Model"
3. Click "Build Model"

### 4. Submit for Certification

1. Complete all required fields
2. Review certification checklist
3. Submit for review
4. Address any feedback

## Troubleshooting

### Common Issues

1. **Account Linking Fails**
   - Verify OAuth endpoints are accessible
   - Check redirect URIs match exactly
   - Verify client ID and secret

2. **Lambda Timeout**
   - Increase Lambda timeout
   - Check CloudWatch logs
   - Optimize database queries

3. **Intent Not Recognized**
   - Check interaction model
   - Verify sample utterances
   - Test with different phrasings

4. **Permission Errors**
   - Verify IAM role permissions
   - Check DynamoDB table access
   - Verify SNS permissions

## Next Steps

- Monitor skill usage in CloudWatch
- Set up alerts for errors
- Collect user feedback
- Plan feature updates

## Resources

- [Alexa Skills Kit Documentation](https://developer.amazon.com/en-US/docs/alexa/ask-overviews/what-is-the-alexa-skills-kit.html)
- [ASK CLI Documentation](https://developer.amazon.com/en-US/docs/alexa/smapi/ask-cli-command-reference.html)
- [Account Linking Guide](https://developer.amazon.com/en-US/docs/alexa/account-linking/understand-account-linking.html)

