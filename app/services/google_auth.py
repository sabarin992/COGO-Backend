from google.oauth2 import id_token
from google.auth.transport import requests
from app.core.config import settings

GOOGLE_CLIENT_ID = settings.GOOGLE_CLIENT_ID

def verify_google_token(token: str):
    try:
        idinfo = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            GOOGLE_CLIENT_ID
        )
        return idinfo
    except Exception:
        return None
    



from fastapi import HTTPException
from app.repositories.user_repo import get_or_create_user
from app.core.security import create_access_token
from google.oauth2 import id_token
from google.auth.transport import requests
from app.core.config import settings   # better practice


def verify_google_token(token: str):
    try:
        idinfo = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            settings.GOOGLE_CLIENT_ID
        )
        return idinfo
    except ValueError:
        return None
    

def google_login(data, db):

    user_info = verify_google_token(data.token)

    if not user_info:
        raise HTTPException(status_code=401, detail="Invalid token")

    email = user_info.get("email")
    name = user_info.get("name")

    # ✅ FIX HERE
    user = get_or_create_user(db, email=email, name=name)

    access_token = create_access_token({"sub": email})
    # refresh_token = create_refresh_token({"user_id": user.id})

    return {
        "access_token": access_token,
        # "refresh_token": refresh_token,
        "user": {
            "email": email,
            "name": name
        }
    }