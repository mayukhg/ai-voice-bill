# API Documentation

## Base URL

```
Development: http://localhost:5000
Production: https://api.yourdomain.com
```

## Authentication

All endpoints require a valid `user_id` which is obtained through Alexa account linking (OAuth 2.0).

## Endpoints

### Health Check

**GET** `/health`

Check if the service is running.

**Response**:
```json
{
  "status": "healthy",
  "service": "ai-voice-bill-payment"
}
```

---

### Get Bill Reminders (Flow 1)

**GET** `/api/v1/reminders/<user_id>`

Get all bill reminders for a user.

**Parameters**:
- `user_id` (path): User identifier

**Response**:
```json
{
  "success": true,
  "message": "Found 2 bill reminders",
  "data": {
    "reminders": [
      {
        "bill_id": "BILL-001",
        "bill_type": "utility",
        "amount": 150.00,
        "due_date": "2024-01-15",
        "text_message": "Hello! This is a reminder that you have a utility bill of $150.00 due on 2024-01-15...",
        "bill_details": {
          "bill_id": "BILL-001",
          "user_id": "user123",
          "bill_type": "utility",
          "amount": 150.00,
          "due_date": "2024-01-15",
          "is_paid": false
        }
      }
    ],
    "count": 2
  },
  "timestamp": "2024-01-10T10:30:00Z"
}
```

**Error Response**:
```json
{
  "success": false,
  "error": {
    "code": "INVALID_USER_ID",
    "message": "Invalid user ID",
    "timestamp": "2024-01-10T10:30:00Z"
  }
}
```

---

### Get Reminder Audio

**GET** `/api/v1/reminders/<user_id>/audio/<bill_id>`

Get audio file (MP3) for a specific bill reminder.

**Parameters**:
- `user_id` (path): User identifier
- `bill_id` (path): Bill identifier

**Response**: MP3 audio stream

**Headers**:
- `Content-Type: audio/mpeg`
- `Content-Disposition: attachment; filename=reminder_BILL-001.mp3`

---

### Get User Bills

**GET** `/api/v1/bills/<user_id>`

Get all unpaid bills for a user.

**Parameters**:
- `user_id` (path): User identifier

**Response**:
```json
{
  "success": true,
  "message": "Bills retrieved successfully",
  "data": {
    "bills": [
      {
        "bill_id": "BILL-001",
        "bill_type": "utility",
        "amount": 150.00,
        "due_date": "2024-01-15",
        "is_paid": false,
        "description": "Electricity bill for December"
      }
    ],
    "count": 1
  },
  "timestamp": "2024-01-10T10:30:00Z"
}
```

---

### Initiate Payment (Flow 2 - Step 1)

**POST** `/api/v1/payments/initiate`

Initiate payment process for a bill. Sends OTP to user's mobile number.

**Request Body**:
```json
{
  "user_id": "user123",
  "bill_id": "BILL-001"
}
```

**Response**:
```json
{
  "success": true,
  "message": "Payment initiated",
  "data": {
    "success": true,
    "bill_id": "BILL-001",
    "bill_type": "utility",
    "amount": 150.00,
    "due_date": "2024-01-15",
    "otp_prompt": "For security purposes, please provide the one-time password...",
    "message": "OTP has been sent to your registered mobile number. For security purposes..."
  },
  "timestamp": "2024-01-10T10:30:00Z"
}
```

**Error Response**:
```json
{
  "success": false,
  "error": {
    "code": "PAYMENT_INIT_ERROR",
    "message": "Bill not found",
    "timestamp": "2024-01-10T10:30:00Z"
  }
}
```

---

### Verify OTP and Process Payment (Flow 2 - Step 2)

**POST** `/api/v1/payments/verify`

Verify OTP and complete payment processing.

**Request Body**:
```json
{
  "user_id": "user123",
  "bill_id": "BILL-001",
  "otp": "123456"
}
```

**Response**:
```json
{
  "success": true,
  "message": "Payment processed successfully",
  "data": {
    "success": true,
    "payment_id": "PAY-20240110103000-a1b2c3d4",
    "amount": 150.00,
    "confirmation_message": "Your payment of $150.00 for your utility bill has been successfully processed...",
    "message": "Payment processed successfully"
  },
  "timestamp": "2024-01-10T10:30:00Z"
}
```

**Error Response**:
```json
{
  "success": false,
  "error": {
    "code": "PAYMENT_VERIFICATION_ERROR",
    "message": "Invalid or expired OTP. Please try again.",
    "timestamp": "2024-01-10T10:30:00Z"
  }
}
```

---

### Lex Fulfillment Webhook

**POST** `/api/v1/lex/fulfillment`

AWS Lex fulfillment endpoint for handling bot interactions.

**Request Body** (Lex format):
```json
{
  "sessionState": {
    "sessionAttributes": {
      "user_id": "user123"
    },
    "intent": {
      "name": "GetBillReminders",
      "slots": {}
    }
  }
}
```

**Response** (Lex format):
```json
{
  "sessionState": {
    "dialogAction": {
      "type": "Close",
      "fulfillmentState": "Fulfilled"
    },
    "intent": {
      "name": "GetBillReminders",
      "state": "Fulfilled"
    }
  },
  "messages": [
    {
      "contentType": "PlainText",
      "content": "You have 2 bills due. Your utility bill of $150.00 is due on 2024-01-15."
    }
  ]
}
```

## Error Codes

| Code | Description |
|------|-------------|
| `INVALID_USER_ID` | User ID is missing or invalid |
| `BILL_NOT_FOUND` | Bill does not exist |
| `MISSING_BILL_ID` | Bill ID not provided |
| `MISSING_OTP` | OTP not provided |
| `PAYMENT_INIT_ERROR` | Error initiating payment |
| `PAYMENT_VERIFICATION_ERROR` | OTP verification failed |
| `AUDIO_GENERATION_ERROR` | Error generating audio |
| `REMINDER_ERROR` | Error retrieving reminders |
| `BILLS_ERROR` | Error retrieving bills |
| `PAYMENT_ERROR` | General payment processing error |
| `GENERAL_ERROR` | General application error |

## Rate Limiting

- 100 requests per minute per user
- 1000 requests per hour per user

## Response Format

All responses follow a consistent format:

**Success**:
```json
{
  "success": true,
  "message": "Operation successful",
  "data": { ... },
  "timestamp": "ISO 8601 timestamp"
}
```

**Error**:
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Error message",
    "timestamp": "ISO 8601 timestamp"
  }
}
```

## Testing

### Using cURL

**Get Reminders**:
```bash
curl -X GET http://localhost:5000/api/v1/reminders/user123
```

**Initiate Payment**:
```bash
curl -X POST http://localhost:5000/api/v1/payments/initiate \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user123", "bill_id": "BILL-001"}'
```

**Verify OTP**:
```bash
curl -X POST http://localhost:5000/api/v1/payments/verify \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user123", "bill_id": "BILL-001", "otp": "123456"}'
```

### Using Python

```python
import requests

base_url = "http://localhost:5000"

# Get reminders
response = requests.get(f"{base_url}/api/v1/reminders/user123")
print(response.json())

# Initiate payment
response = requests.post(
    f"{base_url}/api/v1/payments/initiate",
    json={"user_id": "user123", "bill_id": "BILL-001"}
)
print(response.json())

# Verify OTP
response = requests.post(
    f"{base_url}/api/v1/payments/verify",
    json={"user_id": "user123", "bill_id": "BILL-001", "otp": "123456"}
)
print(response.json())
```

