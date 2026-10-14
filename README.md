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

## Installation and Setup

Follow these steps to set up and run the CoGo backend locally.

### Prerequisites

Make sure the following tools are installed on your system:

- Python 3.10 or a compatible version required by your dependencies
- PostgreSQL
- Redis
- Git
- pip (Python package manager)

### 1. Clone the Repository

```bash
git clone <your-repository-url> (git clone https://github.com/sabarin992/COGO-Backend.git)
cd <your-project-folder>
```

Replace the placeholders with your GitHub repository URL and project folder name.

### 2. Create a Virtual Environment

```bash
python3 -m venv venv
```

Activate the virtual environment on macOS or Linux:

```bash
source venv/bin/activate
```

### 3. Install Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root directory, alongside `alembic.ini` and `requirements.txt`.

Add the environment variables required by your application.

Example:

```env
DATABASE_URL=postgresql://<username>:<password>@localhost:5432/<database_name>

SECRET_KEY=<your-secret-key>
ALGORITHM=HS256

REDIS_URL=redis://localhost:6379/0

GOOGLE_CLIENT_ID=<your-google-client-id>

CLOUDINARY_CLOUD_NAME=<your-cloud-name>
CLOUDINARY_API_KEY=<your-cloudinary-api-key>
CLOUDINARY_API_SECRET=<your-cloudinary-api-secret>
```

Configure any additional variables required for email delivery, OTP verification, and other integrations.

**Important:** The variable names above are examples. Check `app/core/config.py`, `app/core/security.py`, and the relevant service files to confirm the exact names and settings used by your application.

Never commit your actual `.env` file or secret credentials to GitHub.

### 5. Set Up PostgreSQL

Create a PostgreSQL database for the application.

For example, open PostgreSQL and run:

```sql
CREATE DATABASE cogo_db;
```

Update `DATABASE_URL` in your `.env` file with your PostgreSQL username, password, host, port, and database name.

Make sure PostgreSQL is running before starting the application.

### 6. Start Redis

If your application uses Redis for token blacklisting or other features, ensure the Redis server is running.

For a local Redis installation on macOS using Homebrew:

```bash
brew services start redis
```

Verify the connection:

```bash
redis-cli ping
```

A successful response is:

```text
PONG
```

If Redis is already running or hosted remotely, configure the appropriate `REDIS_URL` instead.

### 7. Run Database Migrations

Apply the existing Alembic migrations to create or update the database schema:

```bash
alembic upgrade head
```

This applies the migrations in `alembic/versions/` up to the latest revision.

Run this command from the project root directory, where `alembic.ini` is located.

### 8. Start the FastAPI Server

Run the application using Uvicorn:

```bash
uvicorn app.main:app --reload
```

The backend should be available at:

```text
http://127.0.0.1:8000
```

### 9. Access API Documentation

FastAPI provides interactive API documentation.

- **Swagger UI:** http://127.0.0.1:8000/docs
- **ReDoc:** http://127.0.0.1:8000/redoc

Use these pages to explore and test your API endpoints.

### Troubleshooting

- **Database connection error:** Verify PostgreSQL is running and `DATABASE_URL` is correct.
- **Redis connection error:** Verify Redis is running and `REDIS_URL` is correct.
- **Missing environment variables:** Check your `.env` file and application configuration.
- **Migration errors:** Check the Alembic revision history and database connection settings.
- **Import errors:** Activate your virtual environment and reinstall dependencies.


## Future Improvements

- **Payment Integration:** Integrate Stripe to enable secure online payments for ride-sharing transactions.
- **SOS Management:** Implement an emergency SOS feature to help users request assistance during a ride.
- **Admin Dashboard:** Develop an administrative dashboard to manage users, rides, ride requests, and KYC verification.
- **Sales Reports:** Implement an admin-side sales reporting feature to track revenue, payment transactions, completed rides, and sales performance.

