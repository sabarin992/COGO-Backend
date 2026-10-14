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
- **FastAPI** - Building REST APIs and backend endpoints.
- **Uvicorn** - Running the FastAPI application server.
- **SQLAlchemy** - ORM for interacting with the database.
- **Alembic** - Managing database schema migrations.

### Database
- **PostgreSQL** - Relational database for storing application data.

