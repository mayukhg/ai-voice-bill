# Architecture Documentation

## System Architecture Overview

The AI Voice Bill Payment Service is a serverless architecture built on AWS, designed to provide voice-based bill reminders and payment processing through Amazon Alexa.

## High-Level Architecture

```
┌─────────────┐
│   Amazon    │
│   Alexa     │
│   Device    │
└──────┬──────┘
       │
       │ Voice Input/Output
       │
┌──────▼─────────────────────────────────────┐
│         AWS Lex Bot                        │
│  - Intent Recognition                      │
│  - Slot Filling                            │
│  - Conversation Management                 │
└──────┬─────────────────────────────────────┘
       │
       │ Fulfillment Requests
       │
┌──────▼─────────────────────────────────────┐
│      API Gateway / Lambda                  │
│      Flask Application                      │
│  - Reminder Service (Flow 1)               │
│  - Payment Service (Flow 2)                 │
│  - Lex Fulfillment Handler                  │
└──────┬─────────────────────────────────────┘
       │
       ├──────────────┬──────────────┬──────────────┐
       │              │              │              │
┌──────▼──────┐ ┌─────▼──────┐ ┌─────▼──────┐ ┌───▼──────┐
│  DynamoDB   │ │   AWS      │ │   AWS      │ │   AWS    │
│             │ │   Polly    │ │   SNS      │ │  Lambda  │
│ - Bills     │ │            │ │            │ │          │
│ - Users     │ │ Text-to-   │ │ SMS/OTP    │ │ Scheduled│
│ - Payments  │ │ Speech     │ │ Delivery   │ │ Reminders│
│ - OTP       │ │            │ │            │ │          │
└─────────────┘ └────────────┘ └────────────┘ └──────────┘
```

## Component Details

### 1. Amazon Alexa

**Role**: Voice interface for users
- Captures voice input
- Plays audio responses
- Handles account linking for user authentication

**Integration**: 
- Connected to AWS Lex bot via Alexa Skills Kit
- Account linking provides user_id for session management

### 2. AWS Lex

**Role**: Natural Language Understanding (NLU)
- Processes user utterances
- Recognizes intents (GetBillReminders, PayBill, VerifyOTP)
- Manages conversation flow and slot filling
- Routes to fulfillment endpoint

**Intents**:
- `GetBillReminders`: Retrieves due bills
- `PayBill`: Initiates payment process
- `VerifyOTP`: Verifies OTP and completes payment

### 3. Flask Application (Backend API)

**Role**: Business logic and orchestration

**Services**:
- **ReminderService**: Handles Flow 1 (bill reminders)
  - Queries due bills from DynamoDB
  - Generates reminder messages
  - Creates audio via Polly
  
- **PaymentService**: Handles Flow 2 (payments with OTP)
  - Initiates payment process
  - Generates and sends OTP
  - Verifies OTP and processes payment

**Endpoints**:
- `/api/v1/reminders/<user_id>`: Get reminders
- `/api/v1/payments/initiate`: Start payment
- `/api/v1/payments/verify`: Verify OTP and pay
- `/api/v1/lex/fulfillment`: Lex webhook handler

### 4. AWS Polly

**Role**: Text-to-Speech conversion
- Converts reminder messages to natural-sounding speech
- Generates payment confirmations
- Uses neural engine for high-quality output

**Usage**:
- Reminder audio generation
- Payment confirmation messages
- OTP prompts

### 5. DynamoDB

**Role**: Data persistence

**Tables**:
- **bills**: Bill information
  - Primary Key: `user_id` (Partition), `bill_id` (Sort)
  - Attributes: amount, due_date, bill_type, is_paid, description
  
- **users**: User profiles
  - Primary Key: `user_id`
  - Attributes: phone_number, email, preferences
  
- **payments**: Payment history
  - Primary Key: `payment_id`
  - Attributes: user_id, bill_id, amount, status, payment_date
  
- **otp_records**: OTP storage
  - Primary Key: `user_id` (Partition), `otp` (Sort)
  - Attributes: expiry_time, is_used, created_at

### 6. AWS SNS

**Role**: SMS delivery for OTP
- Sends OTP codes to registered mobile numbers
- Uses SNS topic or direct SMS publishing
- Handles delivery failures gracefully

## Data Flow

### Flow 1: Bill Reminders

1. **Scheduled Trigger** (Lambda or Cron):
   - Queries DynamoDB for bills due within 7 days
   - For each user with due bills:
     - Generates reminder message
     - Converts to speech via Polly
     - Sends to Alexa for delivery

2. **On-Demand Reminder** (User Request):
   - User asks: "What bills are due?"
   - Lex recognizes `GetBillReminders` intent
   - Fulfillment endpoint queries due bills
   - Returns formatted response
   - Alexa speaks the response

### Flow 2: Voice Payment with OTP

1. **Payment Initiation**:
   - User: "I want to pay my bill"
   - Lex recognizes `PayBill` intent
   - Fulfillment endpoint:
     - Validates bill exists
     - Generates 6-digit OTP
     - Saves OTP to DynamoDB (with expiry)
     - Sends OTP via SNS to user's phone
     - Returns prompt for OTP

2. **OTP Verification**:
   - User provides OTP via voice
   - Lex recognizes `VerifyOTP` intent
   - Fulfillment endpoint:
     - Validates OTP (checks expiry, not used)
     - Processes payment (mock payment gateway)
     - Marks bill as paid
     - Saves payment record
     - Returns confirmation message

## Security Architecture

### Authentication
- **Account Linking**: OAuth 2.0 flow between Alexa and backend
- **User Identification**: `user_id` from account linking session

### Authorization
- All operations validate `user_id`
- Users can only access their own bills
- Payment operations require MFA (OTP)

### Data Protection
- **Encryption at Rest**: DynamoDB encryption enabled
- **Encryption in Transit**: HTTPS/TLS for all API calls
- **OTP Security**:
  - Time-limited (5 minutes)
  - Single-use only
  - Stored with expiry timestamp

### Payment Security
- OTP required for all payments
- Payment records logged for audit
- No sensitive payment data stored (tokenized if needed)

## Scalability Considerations

### Horizontal Scaling
- Flask app can run on multiple Lambda instances
- DynamoDB auto-scales based on traffic
- Lex handles concurrent conversations

### Performance Optimization
- DynamoDB queries use indexes for fast lookups
- Polly responses cached where possible
- Async OTP delivery (non-blocking)

### Monitoring
- CloudWatch logs for all services
- API Gateway metrics
- DynamoDB metrics
- Error tracking and alerting

## Deployment Architecture

### Development
- Local Flask server
- AWS services accessed via credentials
- Mock payment gateway

### Production
- Flask app deployed to AWS Lambda or ECS
- API Gateway in front
- All AWS services in same region
- CloudWatch monitoring enabled
- Auto-scaling configured

## Error Handling

### Graceful Degradation
- If Polly fails, return text response
- If SNS fails, log OTP for dev mode
- If DynamoDB fails, return error message

### Retry Logic
- OTP delivery retries (3 attempts)
- Payment processing idempotent
- Session state preserved on errors

## Future Enhancements

1. **Multi-language Support**: Lex and Polly support multiple languages
2. **Voice Biometrics**: Additional authentication layer
3. **Payment Scheduling**: Recurring payment setup
4. **Bill Splitting**: Shared bill payments
5. **Analytics Dashboard**: Payment trends and insights

