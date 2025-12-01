# Bill Payment Assistant - Alexa Skill

This is the Alexa Skill implementation of the AI Voice Bill Payment Service. It allows users to manage and pay bills through natural voice interactions with Amazon Alexa devices.

## 🎯 Features

- **Voice Bill Reminders**: Get proactive reminders for bills due within 7 days
- **Voice Bill Payments**: Pay bills securely using voice commands with OTP verification
- **Payment History**: Check payment status and history
- **Account Linking**: Secure OAuth 2.0 account linking
- **Proactive Events**: Automated bill reminders sent to users

## 📁 Project Structure

```
ai-voice-bill-1/
├── src/
│   ├── alexa/
│   │   ├── __init__.py
│   │   ├── lambda_function.py      # Main Lambda handler
│   │   ├── oauth.py                # OAuth 2.0 endpoints
│   │   ├── proactive_events.py    # Proactive Events API
│   │   ├── session_manager.py     # Session management
│   │   ├── error_handler.py      # Error handling
│   │   └── interaction_model.json # Intent schema
│   ├── services/                   # Business logic services
│   ├── aws_services/               # AWS service integrations
│   └── utils/                      # Utility functions
├── skill.json                      # Skill manifest
├── skill-icons/                    # Skill icons and images
├── privacy-policy.html             # Privacy policy
├── terms-of-service.html           # Terms of service
├── lambda_deploy.sh               # Lambda deployment script
├── ask-cli-config.json            # ASK CLI configuration
├── ALEXA_SKILL_REQUIREMENTS.md    # Complete requirements
├── ALEXA_DEPLOYMENT.md            # Deployment guide
└── ALEXA_SETUP_GUIDE.md           # Setup guide
```

## 🚀 Quick Start

### 1. Prerequisites

- Amazon Developer Account
- AWS Account
- Python 3.9+
- Node.js 14+ (for ASK CLI)
- AWS CLI configured

### 2. Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Install ASK CLI
npm install -g ask-cli
ask configure

# Configure environment
cp .env.example .env
# Edit .env with your configuration
```

### 3. Setup AWS Resources

See `ALEXA_SETUP_GUIDE.md` for detailed instructions on:
- Creating DynamoDB tables
- Setting up IAM roles
- Configuring SNS

### 4. Deploy Lambda Function

```bash
chmod +x lambda_deploy.sh
export LAMBDA_ROLE_ARN="arn:aws:iam::ACCOUNT_ID:role/lambda-execution-role"
./lambda_deploy.sh
```

### 5. Configure Skill in Developer Console

1. Create skill at https://developer.amazon.com/alexa/console/ask
2. Upload `skill.json` and `interaction_model.json`
3. Configure account linking
4. Set up privacy policy and terms URLs

See `ALEXA_SETUP_GUIDE.md` for detailed steps.

## 📚 Documentation

- **ALEXA_SKILL_REQUIREMENTS.md**: Complete requirements document (200+ requirements)
- **ALEXA_DEPLOYMENT.md**: Step-by-step deployment guide
- **ALEXA_SETUP_GUIDE.md**: Initial setup and configuration guide
- **ALEXA_SKILL_REQUIREMENTS_SUMMARY.md**: Executive summary

## 🔧 Configuration

### Environment Variables

Key environment variables (see `.env.example`):

```env
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret

# OAuth Configuration
OAUTH_CLIENT_ID=your_client_id
OAUTH_CLIENT_SECRET=your_client_secret

# Alexa Configuration
ALEXA_CLIENT_ID=your_lwa_client_id
ALEXA_CLIENT_SECRET=your_lwa_client_secret
ALEXA_SKILL_ID=amzn1.ask.skill.YOUR_SKILL_ID
```

### Skill Manifest

Update `skill.json` with:
- Your AWS account ID
- Lambda function ARN
- Skill ID
- Icon URLs
- Privacy policy and terms URLs

## 🧪 Testing

### Test in Developer Console

1. Go to "Test" tab in Developer Console
2. Enable testing
3. Test all intents:
   - "open bill payment"
   - "what bills are due?"
   - "pay my utility bill"
   - "check payment status"

### Test on Device

1. Enable skill in Alexa app
2. Link account
3. Say: "Alexa, open bill payment"
4. Test all features

## 📋 Intents

### Built-in Intents

- **LaunchRequest**: Welcome message
- **AMAZON.HelpIntent**: Help information
- **AMAZON.CancelIntent**: Cancel operation
- **AMAZON.StopIntent**: Stop skill
- **AMAZON.FallbackIntent**: Handle unrecognized input

### Custom Intents

- **GetBillReminders**: Get bills due within 7 days
- **PayBill**: Initiate bill payment
- **VerifyOTP**: Verify OTP and complete payment
- **ListBills**: List all unpaid bills
- **PaymentStatus**: Check payment history

## 🔐 Security

- **OAuth 2.0**: Secure account linking
- **OTP Verification**: Multi-factor authentication for payments
- **Encryption**: Data encrypted at rest and in transit
- **Token Management**: Secure token storage and validation

## 🚢 Deployment

See `ALEXA_DEPLOYMENT.md` for complete deployment instructions.

Quick deployment:

```bash
# Deploy Lambda
./lambda_deploy.sh

# Deploy skill
ask deploy
```

## 📊 Monitoring

- **CloudWatch Logs**: All Lambda function logs
- **CloudWatch Metrics**: Function performance metrics
- **Alexa Analytics**: Skill usage analytics in Developer Console

## 🐛 Troubleshooting

### Common Issues

1. **Account Linking Fails**
   - Verify OAuth endpoints are accessible via HTTPS
   - Check redirect URIs match exactly
   - Verify client credentials

2. **Lambda Timeout**
   - Increase Lambda timeout (max 8 seconds for ASK)
   - Optimize database queries
   - Check CloudWatch logs

3. **Intent Not Recognized**
   - Verify interaction model is built
   - Check sample utterances
   - Test with different phrasings

## 📝 Certification Checklist

Before submitting for certification:

- [ ] All required intents implemented
- [ ] Account linking works correctly
- [ ] Privacy policy and terms accessible
- [ ] No crashes or errors
- [ ] Help intent works
- [ ] Stop/Cancel intents work
- [ ] Fallback intent works
- [ ] Error handling is robust
- [ ] Testing instructions provided
- [ ] Icons and images uploaded

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🔗 Resources

- [Alexa Skills Kit Documentation](https://developer.amazon.com/en-US/docs/alexa/ask-overviews/what-is-the-alexa-skills-kit.html)
- [ASK SDK for Python](https://github.com/alexa/alexa-skills-kit-sdk-for-python)
- [Account Linking Guide](https://developer.amazon.com/en-US/docs/alexa/account-linking/understand-account-linking.html)
- [Proactive Events API](https://developer.amazon.com/en-US/docs/alexa/smapi/proactive-events-api.html)

## 📞 Support

For issues or questions:
- Open an issue on GitHub
- Check documentation in `ALEXA_SKILL_REQUIREMENTS.md`
- Review setup guide in `ALEXA_SETUP_GUIDE.md`

