from fastapi import Request,Depends,HTTPException
from sqlalchemy.orm import Session
from app.db.deps import get_db
from app.core.security import verify_token

def get_current_user(request: Request, db: Session = Depends(get_db)):

    token = request.cookies.get("access_token")


    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    # remove "Bearer " if you added it
    if token.startswith("Bearer "):
        token = token.split(" ")[1]

    payload = verify_token(token)

    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    email = payload.get("sub")

    if not email:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    # user = get_user_by_email(db, email)

    # if not user:
    #     raise HTTPException(status_code=401, detail="User not found")

    return email
