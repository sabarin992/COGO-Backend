from jose import jwt,JWTError
from datetime import datetime,timedelta,timezone
from app.core.config import settings


def create_access_token(data:dict):
    payload = data.copy()
    expiry = datetime.now((timezone.utc))+timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload.update({"exp":expiry,"type":"access_token"})
    token = jwt.encode(payload,settings.SECRET_KEY,algorithm=settings.ALGORITHM)
    return token