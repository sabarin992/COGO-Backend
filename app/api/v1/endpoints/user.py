from fastapi import APIRouter,Request,Depends
from app.api.deps import get_current_user


router = APIRouter()


@router.get("/profile")
def profile(request:Request,user=Depends(get_current_user)):
    return {"user_email":user}


@router.get("/check-auth")
def check_auth(user=Depends(get_current_user)):
    return user