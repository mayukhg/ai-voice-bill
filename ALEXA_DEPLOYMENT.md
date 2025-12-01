# Alexa Skill Deployment Guide

This guide covers deploying the Bill Payment Assistant Alexa Skill to production.

## Prerequisites

1. **Amazon Developer Account**
   - Sign up at https://developer.amazon.com
   - Complete account verification

2. **AWS Account**
   - AWS account with appropriate permissions
   - AWS CLI configured

3. **ASK CLI**
   ```bash
   npm install -g ask-cli
   ask configure
   ```

4. **Required Environment Variables**
   - See `.env.example` for all required variables

## Deployment Steps

### Step 1: Deploy Lambda Function

#### Option A: Using Deployment Script

```bash
# Set environment variables
export LAMBDA_ROLE_ARN="arn:aws:iam::ACCOUNT_ID:role/lambda-execution-role"
export AWS_REGION="us-east-1"
export BILLS_TABLE="bills"
export USERS_TABLE="users"
export PAYMENTS_TABLE="payments"
export OTP_TABLE="otp_records"

# Run deployment script
chmod +x lambda_deploy.sh
./lambda_deploy.sh
```

#### Option B: Manual Deployment

1. **Create deployment package:**
   ```bash
   zip -r function.zip src/ requirements.txt
   ```

2. **Create Lambda function:**
   ```bash
   aws lambda create-function \
     --function-name alexa-bill-payment-skill \
     --runtime python3.9 \
     --role arn:aws:iam::ACCOUNT_ID:role/lambda-execution-role \
     --handler src.alexa.lambda_function.lambda_handler \
     --zip-file fileb://function.zip \
     --timeout 30 \
     --memory-size 512
   ```

3. **Update function code:**
   ```bash
   aws lambda update-function-code \
     --function-name alexa-bill-payment-skill \
     --zip-file fileb://function.zip
   ```

### Step 2: Configure IAM Role

Create IAM role with permissions for:
- DynamoDB (read/write)
- SNS (send SMS)
- Polly (synthesize speech)
- CloudWatch Logs

Example policy:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:UpdateItem",
        "dynamodb:Query",
        "dynamodb:Scan"
      ],
      "Resource": [
        "arn:aws:dynamodb:*:*:table/bills",
        "arn:aws:dynamodb:*:*:table/users",
        "arn:aws:dynamodb:*:*:table/payments",
        "arn:aws:dynamodb:*:*:table/otp_records"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "sns:Publish"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "polly:SynthesizeSpeech"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    }
  ]
}
```

### Step 3: Deploy Skill Manifest

1. **Update skill.json:**
   - Replace `ACCOUNT_ID` with your AWS account ID
   - Update Lambda function ARN
   - Update redirect URLs with your skill ID
   - Update icon URLs (host icons on your domain)

2. **Deploy using ASK CLI:**
   ```bash
   ask deploy
   ```

   Or manually upload in Alexa Developer Console:
   - Go to https://developer.amazon.com/alexa/console/ask
   - Create new skill or open existing
   - Upload `skill.json` and `interaction_model.json`

### Step 4: Configure Account Linking

1. **Set up OAuth endpoints:**
   - Deploy Flask app with OAuth routes
   - Ensure endpoints are publicly accessible via HTTPS
   - Update `skill.json` with correct URLs

2. **Configure in Developer Console:**
   - Go to Build → Account Linking
   - Select "Auth Code Grant"
   - Enter:
     - Authorization URL: `https://your-domain.com/oauth/authorize`
     - Access Token URL: `https://your-domain.com/oauth/token`
     - Client ID and Secret
   - Add redirect URLs

### Step 5: Host Privacy Policy and Terms

1. **Upload to web server:**
   - Upload `privacy-policy.html` and `terms-of-service.html`
   - Ensure HTTPS access
   - Update URLs in `skill.json`

2. **Verify accessibility:**
   ```bash
   curl https://your-domain.com/privacy-policy
   curl https://your-domain.com/terms-of-service
   ```

### Step 6: Deploy Proactive Events Lambda

1. **Create proactive events function:**
   ```bash
   zip -r proactive.zip src/alexa/proactive_events.py src/services/ src/aws_services/ src/utils/ src/config.py requirements.txt
   
   aws lambda create-function \
     --function-name alexa-bill-payment-proactive \
     --runtime python3.9 \
     --role arn:aws:iam::ACCOUNT_ID:role/lambda-execution-role \
     --handler src.alexa.proactive_events.lambda_handler \
     --zip-file fileb://proactive.zip \
     --timeout 60 \
     --memory-size 256
   ```

2. **Set up EventBridge rule for scheduled reminders:**
   ```bash
   aws events put-rule \
     --name daily-bill-reminders \
     --schedule-expression "cron(0 9 * * ? *)" \
     --state ENABLED
   
   aws lambda add-permission \
     --function-name alexa-bill-payment-proactive \
     --statement-id allow-eventbridge \
     --action lambda:InvokeFunction \
     --principal events.amazonaws.com \
     --source-arn arn:aws:events:REGION:ACCOUNT_ID:rule/daily-bill-reminders
   
   aws events put-targets \
     --rule daily-bill-reminders \
     --targets "Id=1,Arn=arn:aws:lambda:REGION:ACCOUNT_ID:function:alexa-bill-payment-proactive"
   ```

### Step 7: Test the Skill

1. **Enable skill in Alexa app**
2. **Link account**
3. **Test all intents:**
   - "Alexa, open bill payment"
   - "What bills are due?"
   - "Pay my utility bill"
   - "Check payment status"

### Step 8: Submit for Certification

1. **Complete skill information:**
   - Fill all required fields in Developer Console
   - Upload icons and images
   - Complete testing instructions

2. **Submit for review:**
   - Go to Distribution → Certification
   - Review all requirements
   - Submit for certification

3. **Address feedback:**
   - Respond to certification team questions
   - Fix any issues identified
   - Resubmit if needed

## Environment Variables

Create `.env` file with:

```env
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret

# DynamoDB Tables
BILLS_TABLE=bills
USERS_TABLE=users
PAYMENTS_TABLE=payments
OTP_TABLE=otp_records

# OAuth Configuration
OAUTH_CLIENT_ID=your_client_id
OAUTH_CLIENT_SECRET=your_client_secret
OAUTH_REDIRECT_URI=https://pitangui.amazon.com/api/skill/link/YOUR_SKILL_ID

# Alexa Configuration
ALEXA_CLIENT_ID=your_lwa_client_id
ALEXA_CLIENT_SECRET=your_lwa_client_secret
ALEXA_SKILL_ID=amzn1.ask.skill.YOUR_SKILL_ID

# Lambda Configuration
LAMBDA_FUNCTION_NAME=alexa-bill-payment-skill
LAMBDA_PROACTIVE_FUNCTION_NAME=alexa-bill-payment-proactive
```

## Troubleshooting

### Lambda Function Issues

- **Check CloudWatch Logs:**
  ```bash
  aws logs tail /aws/lambda/alexa-bill-payment-skill --follow
  ```

- **Test function locally:**
  ```bash
  python -m pytest tests/test_lambda.py
  ```

### Account Linking Issues

- **Verify OAuth endpoints:**
  ```bash
  curl https://your-domain.com/oauth/authorize?client_id=test&response_type=code
  ```

- **Check token validation:**
  ```bash
  curl -X POST https://your-domain.com/oauth/validate \
    -H "Content-Type: application/json" \
    -d '{"access_token": "test"}'
  ```

### Skill Certification Issues

- Review certification checklist in `ALEXA_SKILL_REQUIREMENTS.md`
- Ensure all required intents are implemented
- Verify privacy policy and terms are accessible
- Test on physical devices

## Next Steps

1. Monitor skill usage in CloudWatch
2. Set up alerts for errors
3. Collect user feedback
4. Plan feature updates

## Resources

- [Alexa Skills Kit Documentation](https://developer.amazon.com/en-US/docs/alexa/ask-overviews/what-is-the-alexa-skills-kit.html)
- [ASK CLI Documentation](https://developer.amazon.com/en-US/docs/alexa/smapi/ask-cli-command-reference.html)
- [Lambda Deployment Guide](https://docs.aws.amazon.com/lambda/latest/dg/python-package.html)

