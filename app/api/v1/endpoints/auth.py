from fastapi import APIRouter,HTTPException
from app.schemas.auth import LoginRequest


router = APIRouter()


dummy_details = {'username':'sabarinathem','password':'Sabari@1996'}

@router.post("/login")
def login(data:LoginRequest):
    if data.username != dummy_details["username"] or data.password!= dummy_details["password"]:
        raise HTTPException(status_code=401,detail="Invalid credentials")
    return {"message":"Login Successful"}