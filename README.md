# Ride Sharing Application - Backend

## About the Project

This is the backend of my Ride Sharing Application. It is built using **FastAPI** and **PostgreSQL**. The backend provides APIs for user authentication, KYC verification, profile management, and ride management.

---

## Features

* User Registration
* User Login
* Google Login
* Email OTP Verification
* Forgot Password
* Reset Password
* JWT Authentication
* Refresh Token
* Profile Management
* KYC Verification
* Cloudinary Image Upload
* Ride Management

---

## Technologies Used

* FastAPI
* Python
* SQLAlchemy
* PostgreSQL
* Alembic
* JWT
* Pydantic
* Cloudinary

---

## Installation

1. Clone the Repository
git clone <repository-url>
cd backend
2. Create a Virtual Environment
python -m venv venv
3. Activate the Virtual Environment

Windows

venv\Scripts\activate

macOS / Linux

source venv/bin/activate
4. Install Required Dependencies
pip install \
aiosmtplib==5.1.0 \
alembic==1.18.5 \
annotated-doc==0.0.4 \
annotated-types==0.7.0 \
anyio==4.13.0 \
argon2-cffi==25.1.0 \
argon2-cffi-bindings==25.1.0 \
bcrypt==5.0.0 \
blinker==1.9.0 \
certifi==2026.4.22 \
cffi==2.0.0 \
charset-normalizer==3.4.7 \
click==8.3.3 \
cloudinary==1.44.2 \
cryptography==47.0.0 \
dnspython==2.8.0 \
ecdsa==0.19.2 \
email-validator==2.3.0 \
fastapi==0.136.1 \
fastapi-mail==1.6.3 \
google-auth==2.50.0 \
h11==0.16.0 \
httpcore==1.0.9 \
httpx==0.28.1 \
idna==3.13 \
Jinja2==3.1.6 \
Mako==1.3.12 \
MarkupSafe==3.0.3 \
passlib==1.7.4 \
phonenumbers==9.0.29 \
psycopg2==2.9.12 \
pyasn1==0.6.3 \
pyasn1_modules==0.4.2 \
pycparser==3.0 \
pydantic==2.13.3 \
pydantic_core==2.46.3 \
pydantic-settings==2.14.0 \
python-dotenv==1.2.2 \
python-jose==3.5.0 \
python-multipart==0.0.32 \
redis==7.4.0 \
regex==2026.4.4 \
requests==2.33.1 \
rsa==4.9.1 \
six==1.17.0 \
SQLAlchemy==2.0.49 \
starlette==1.0.0 \
typing_extensions==4.15.0 \
typing-inspection==0.4.2 \
urllib3==2.6.3 \
uvicorn==0.46.0

---

## Environment Variables

Create a `.env` file and add the following:

```env
DATABASE_URL=
SECRET_KEY=
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=
```

---

## Database Migration

Create a migration:

```bash
alembic revision --autogenerate -m "Initial migration"
```

Apply the migration:

```bash
alembic upgrade head
```

---

## Run the Server

```bash
uvicorn app.main:app --reload
```

The server will run at:

```text
http://127.0.0.1:8000
```

---

## API Documentation

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

ReDoc:

```text
http://127.0.0.1:8000/redoc
```

---

## Project Structure

```text
├── __pycache__
│   └── main.cpython-314.pyc
├── alembic
│   ├── __pycache__
│   │   └── env.cpython-314.pyc
│   ├── env.py
│   ├── README
│   ├── script.py.mako
│   └── versions
│       ├── 2ae386c2d3eb_added_rejection_reason_field_in_kyc_.py
│       ├── 6c13dc7310fe_create_vehicle_table.py
│       ├── 89c8865497e5_changed_the_is_verified_field_s_data_.py
│       ├── 945cebacec9d_create_vehicle_table.py
│       ├── a659c4a53b33_create_rides_table.py
│       ├── d34b9097b477_create_vehicle_table.py
│       ├── e8a85ec15864_initial_migration.py
│       └── fe62d774da43_add_cloudinary_url_and_public_id_fields_.py
├── alembic.ini
├── app
│   ├── __init__.py
│   ├── __pycache__
│   │   ├── __init__.cpython-314.pyc
│   │   └── main.cpython-314.pyc
│   ├── api
│   │   ├── __pycache__
│   │   │   └── deps.cpython-314.pyc
│   │   ├── deps.py
│   │   └── v1
│   │       ├── __pycache__
│   │       │   └── router.cpython-314.pyc
│   │       ├── endpoints
│   │       │   ├── __pycache__
│   │       │   │   ├── auth.cpython-314.pyc
│   │       │   │   ├── kyc.cpython-314.pyc
│   │       │   │   ├── otp.cpython-314.pyc
│   │       │   │   ├── ride.cpython-314.pyc
│   │       │   │   ├── user.cpython-314.pyc
│   │       │   │   └── vehicle.cpython-314.pyc
│   │       │   ├── auth.py
│   │       │   ├── kyc.py
│   │       │   ├── otp.py
│   │       │   ├── ride.py
│   │       │   ├── user.py
│   │       │   └── vehicle.py
│   │       └── router.py
│   ├── core
│   │   ├── __pycache__
│   │   │   ├── config.cpython-314.pyc
│   │   │   ├── exceptions.cpython-314.pyc
│   │   │   ├── redis.cpython-314.pyc
│   │   │   ├── security.cpython-314.pyc
│   │   │   └── token_blacklist.cpython-314.pyc
│   │   ├── config.py
│   │   ├── exceptions.py
│   │   ├── redis.py
│   │   ├── security.py
│   │   └── token_blacklist.py
│   ├── db
│   │   ├── __pycache__
│   │   │   ├── base.cpython-314.pyc
│   │   │   ├── deps.cpython-314.pyc
│   │   │   └── session.cpython-314.pyc
│   │   ├── base.py
│   │   ├── deps.py
│   │   └── session.py
│   ├── main.py
│   ├── models
│   │   ├── __pycache__
│   │   │   ├── kyc_docs.cpython-314.pyc
│   │   │   ├── ride.cpython-314.pyc
│   │   │   ├── user.cpython-314.pyc
│   │   │   └── vehicle.cpython-314.pyc
│   │   ├── kyc_docs.py
│   │   ├── ride.py
│   │   ├── user.py
│   │   └── vehicle.py
│   ├── repositories
│   │   ├── __pycache__
│   │   │   ├── kyc_repo.cpython-314.pyc
│   │   │   ├── ride_repo.cpython-314.pyc
│   │   │   ├── user_repo.cpython-314.pyc
│   │   │   └── vehicle_repo.cpython-314.pyc
│   │   ├── kyc_repo.py
│   │   ├── ride_repo.py
│   │   ├── user_repo.py
│   │   └── vehicle_repo.py
│   ├── schemas
│   │   ├── __pycache__
│   │   │   ├── auth.cpython-314.pyc
│   │   │   ├── kyc.cpython-314.pyc
│   │   │   ├── otp.cpython-314.pyc
│   │   │   ├── ride.cpython-314.pyc
│   │   │   ├── user.cpython-314.pyc
│   │   │   └── vehicle.cpython-314.pyc
│   │   ├── auth.py
│   │   ├── kyc.py
│   │   ├── otp.py
│   │   ├── ride.py
│   │   ├── user.py
│   │   └── vehicle.py
│   ├── services
│   │   ├── __pycache__
│   │   │   ├── auth_service.cpython-314.pyc
│   │   │   ├── google_auth.cpython-314.pyc
│   │   │   ├── kyc_service.cpython-314.pyc
│   │   │   ├── otp_service.cpython-314.pyc
│   │   │   ├── ride_service.cpython-314.pyc
│   │   │   ├── user_service.cpython-314.pyc
│   │   │   └── vehicle_service.cpython-314.pyc
│   │   ├── auth_service.py
│   │   ├── google_auth.py
│   │   ├── kyc_service.py
│   │   ├── otp_service.py
│   │   ├── ride_service.py
│   │   ├── user_service.py
│   │   └── vehicle_service.py
│   └── utils
│       ├── __pycache__
│       │   ├── cloudinary.cpython-314.pyc
│       │   ├── email.cpython-314.pyc
│       │   └── otp.cpython-314.pyc
│       ├── cloudinary.py
│       ├── email.py
│       └── otp.py
└── tests
```

---

## Future Improvements

* Real-time ride tracking
* Payment integration
* Notifications
* Chat feature
* Ride ratings and reviews

---

## License

This project is created for learning purposes.
