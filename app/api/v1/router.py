from fastapi import APIRouter
from app.api.v1.endpoints import auth, user, otp, kyc, vehicle, ride, chat, recurring_ride, admin_ride, admin_booking, location

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(user.router, prefix="/user", tags=["User"])
api_router.include_router(otp.router, prefix="/otp", tags=["OTP"])
api_router.include_router(kyc.router, prefix="/kyc", tags=["KYC"])
api_router.include_router(vehicle.router, prefix="/vehicles", tags=["Vehicles"])
api_router.include_router(vehicle.router, prefix="/vehicle", tags=["Vehicle"])
api_router.include_router(ride.router, prefix="/ride", tags=["Ride"])
api_router.include_router(admin_ride.router, prefix="/admin/rides", tags=["Admin Rides"])
api_router.include_router(admin_booking.router, prefix="/admin/bookings", tags=["Admin Bookings"])
api_router.include_router(recurring_ride.router, prefix="/recurring-rides", tags=["Recurring Rides"])
api_router.include_router(chat.router, prefix="/chat", tags=["Chat"])
api_router.include_router(location.router, prefix="/location", tags=["Location"])
