from fastapi import APIRouter,HTTPException


router = APIRouter()


dummy_details = {'username':'sabarinathem','password':'Sabari@1996'}

@router.post("/login")
def login(username:str,password:str):
    if username != dummy_details["username"] or password != dummy_details["password"]:
        raise HTTPException(status_code=401,detail="Invalid credentials")
    return {"message":"Login Successful"}