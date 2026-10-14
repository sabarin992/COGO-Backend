# COGO - Ride Sharing Application - Backend

CoGo is a ride-sharing application that connects drivers with passengers traveling in the same direction. Drivers can post rides by adding the source, destination, route, date, and time. Passengers can search for rides and request to join a suitable ride.
CoGo helps drivers and passengers share travel expenses, making journeys more affordable and convenient.

## Features

### Authentication and Security
- User Registration and Login
- Admin Login
- Google Authentication
- JWT Authentication with Access and Refresh Tokens
- Secure Logout and Token Blacklisting
- OTP Verification and Resending
- Password Reset

### User Management
- User Profile Management
- Email Update with OTP Verification
- User Management (Admin)
- Block and Unblock Users (Admin)

### KYC Verification
- KYC Document Upload
- KYC Status Tracking
- KYC Approval and Rejection (Admin)

### Vehicle Management
- Add Vehicle
- View Vehicles
- Edit Vehicle Details
- Delete Vehicle

### Ride Management
- Post a Ride
- View My Rides
- Edit Ride Details
- Delete a Ride
- View Ride Details
- Ride Search and Matching

### Ride Request Management
- Send Ride Requests
- View Received Ride Requests
- View My Bookings
- Accept Ride Requests
- Reject Ride Requests
- Cancel Ride Requests

### Ride Status Management
- Start a Ride
- Mark Arrival at Pickup Point
- Passenger Pickup Management
- Complete a Ride

### Real-Time Communication
- Real-Time Chat Using WebSockets
- Send and Receive Messages
- Chat Message History
- Conversation Management

### Live Location Tracking
- Real-Time Driver Location Sharing
- Live Location Updates Using WebSockets
- Ride-Based Location Access Control
  

## Technology Stack

### Backend
- **FastAPI** – Building REST APIs and backend application logic.
- **Uvicorn** – ASGI server for running the FastAPI application.
- **Starlette** – Provides the underlying ASGI functionality used by FastAPI.
- **Pydantic** – Data validation, request handling, and response schemas.
- **Pydantic Settings** – Managing application configuration and environment settings.

### Database
- **PostgreSQL** – Relational database for storing application data.
- **SQLAlchemy** – ORM for database operations and model management.
- **Alembic** – Managing database schema migrations.
- **Psycopg2** – PostgreSQL database adapter for Python.

### Authentication & Security
- **Python-JOSE** – JWT creation and verification.
- **Argon2-CFFI** – Password hashing using Argon2.
- **Passlib** – Password hashing utilities.
- **Cryptography** – Cryptographic operations.
- **Google Auth** – Google authentication integration.
- **Email Validator** – Email address validation.
- **Phonenumbers** – Phone number parsing and validation.

### Email & Notifications
- **FastAPI-Mail** – Email integration for the FastAPI application.
- **aiosmtplib** – Asynchronous SMTP email delivery.

### File & Image Management
- **Cloudinary** – Cloud-based image and media storage and management.
- **Python Multipart** – Handling multipart form data and file uploads.

### Caching & Real-Time Communication
- **Redis** – In-memory data storage for caching or other application features, depending on your implementation.
- **WebSockets** – Real-time, bidirectional communication.
- **Websockets** – Python library for WebSocket communication.

### HTTP & External Integrations
- **HTTPX** – HTTP client for communicating with external services.
- **Requests** – HTTP requests to external APIs.
- **Google Auth** – Integration with Google authentication services.

### Configuration & Utilities
- **Python-Dotenv** – Loading environment variables from `.env` files.
- **Jinja2** – Template rendering.
- **PyYAML** – Reading and writing YAML configuration files.


## Project Structure

```text
.
├── alembic/
│   ├── versions/                  # Database migration history
│   ├── env.py                     # Migration environment configuration
│   └── script.py.mako             # Migration file template
├── app/
│   ├── api/
│   │   ├── deps.py                # API dependencies
│   │   └── v1/
│   │       ├── endpoints/         # API endpoint handlers
│   │       │   ├── auth.py
│   │       │   ├── chat.py
│   │       │   ├── kyc.py
│   │       │   ├── location.py
│   │       │   ├── otp.py
│   │       │   ├── ride.py
│   │       │   ├── user.py
│   │       │   └── vehicle.py
│   │       └── router.py          # API route registration
│   ├── core/
│   │   ├── config.py              # Application configuration
│   │   ├── exceptions.py          # Custom exceptions
│   │   ├── redis.py               # Redis configuration
│   │   ├── security.py            # Authentication and security
│   │   └── token_blacklist.py     # Token blacklist management
│   ├── db/
│   │   ├── base.py                # SQLAlchemy model registration
│   │   ├── deps.py                # Database dependencies
│   │   └── session.py             # Database session configuration
│   ├── models/                    # SQLAlchemy database models
│   │   ├── chat_conversation.py
│   │   ├── chat_message.py
│   │   ├── kyc_docs.py
│   │   ├── ride_request.py
│   │   ├── ride.py
│   │   ├── user.py
│   │   └── vehicle.py
│   ├── schemas/                   # Pydantic request and response schemas
│   ├── repositories/              # Database query operations
│   ├── services/                  # Business logic
│   ├── utils/                     # Shared utility functions
│   ├── websocket/                 # WebSocket connection and location management
│   ├── __init__.py
│   └── main.py                    # FastAPI application entry point
├── tests/                         # Automated tests
├── alembic.ini                    # Alembic configuration
├── requirements.txt               # Python dependencies
└── README.md                      # Project documentation
```

