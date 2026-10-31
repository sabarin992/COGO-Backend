

# CoGo – Ride Sharing Application (Backend)

CoGo is a ride-sharing platform that connects drivers and passengers traveling in the same direction. Drivers can publish rides, while passengers can search for matching routes and request to join.

Built with **FastAPI** and **PostgreSQL**, CoGo provides ride management, secure authentication, real-time chat, and live location tracking.

## Features

- **Authentication:** JWT access and refresh tokens, Google OAuth, OTP verification, password reset, and token blacklisting.
- **User Management:** Profile management, email verification, and admin user controls.
- **KYC Verification:** Document uploads, verification status, and admin approval/rejection.
- **Vehicle Management:** Add, update, view, and delete vehicles.
- **Ride Management:** Post, update, delete, search, and view rides.
- **Ride Matching:** Find rides based on source, destination, and intermediate routes.
- **Ride Requests:** Send, accept, reject, and cancel ride requests.
- **Ride Status:** Manage pickup, ride start, and ride completion.
- **Real-Time Chat:** WebSocket-based messaging and conversation history.
- **Live Location:** Real-time driver location sharing with ride-based access control.

## Tech Stack

| Category | Technologies |
|---|---|
| Backend | Python, FastAPI, Uvicorn |
| Database | PostgreSQL, SQLAlchemy |
| Migrations | Alembic |
| Validation | Pydantic |
| Authentication | JWT, Python-JOSE, Argon2, Google OAuth |
| Real-Time | WebSockets |
| Caching | Redis |
| File Storage | Cloudinary |
| Email | FastAPI-Mail, aiosmtplib |
| HTTP Client | HTTPX, Requests |

## Project Structure

```text
COGO-Backend/
├── alembic/
│   └── versions/
├── app/
│   ├── api/
│   │   ├── deps.py
│   │   └── v1/
│   │       ├── endpoints/
│   │       └── router.py
│   ├── core/
│   ├── db/
│   ├── models/
│   ├── schemas/
│   ├── repositories/
│   ├── services/
│   ├── utils/
│   ├── websocket/
│   └── main.py
├── tests/
├── alembic.ini
├── requirements.txt
└── README.md
```

## Installation & Setup

### Prerequisites

- Python 3.10+
- PostgreSQL
- Redis
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/sabarin992/COGO-Backend.git

cd COGO-Backend
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv

source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root and configure the required credentials.

```env
SECRET_KEY=your_secret_key
DATABASE_URL=postgresql://username:password@localhost:5432/cogo_db
REDIS_URL=redis://localhost:6379/0
FRONTEND_ORIGIN=http://localhost:5173

GOOGLE_CLIENT_ID=your_google_client_id

CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret

APP_PASSWORD=your_email_app_password
```

### 5. Set Up Database

Create the PostgreSQL database:

```sql
CREATE DATABASE cogo_db;
```

Apply database migrations:

```bash
alembic upgrade head
```

### 6. Start Redis

```bash
brew services start redis
```

Verify Redis:

```bash
redis-cli ping
```

### 7. Run the Application

```bash
uvicorn app.main:app --reload
```

## API Documentation

Once the server is running:

| Documentation | URL |
|---|---|
| Swagger UI | http://127.0.0.1:8000/docs |
| ReDoc | http://127.0.0.1:8000/redoc |

## Future Improvements

- Stripe payment integration.
- Emergency SOS management.
- Admin dashboard and analytics.
- Sales and transaction reports.

## Security

- Keep all credentials and API keys in environment variables.
- Never commit `.env` files or sensitive credentials.
- Use `.env.example` to document required environment variables.