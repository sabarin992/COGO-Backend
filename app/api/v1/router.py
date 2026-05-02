from fastapi import APIRouter
from app.api.v1.endpoints import auth,user,otp


api_router = APIRouter()

api_router.include_router(auth.router,prefix="/auth",tags=["Auth"])
api_router.include_router(user.router,prefix="/user",tags=["User"])
api_router.include_router(otp.router,prefix="/otp",tags=["OTP"])

