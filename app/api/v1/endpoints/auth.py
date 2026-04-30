from fastapi import APIRouter,HTTPException,Response
from app.schemas.auth import LoginRequest
from app.core.security import create_access_token


router = APIRouter()


dummy_details = {'email':'sabarin992@gmail.com','password':'Sabari@1996'}

@router.post("/login")
def login(data:LoginRequest,response:Response):
    

    if data.email != dummy_details["email"] or data.password!= dummy_details["password"]:
        raise HTTPException(status_code=401,detail="Invalid credentials")

    token = create_access_token({"sub":data.email})

    response.set_cookie(
        key="access_token",
        value="token",
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=900
    )
   
    return {"message":"Login Successful"}