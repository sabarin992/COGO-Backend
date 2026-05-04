from jose import jwt,JWTError
from datetime import datetime,timedelta,timezone
from app.core.config import settings
from passlib.context import CryptContext


def create_access_token(data: dict):
    payload = data.copy()

    if "sub" not in payload:
        raise ValueError("Token must contain 'sub'")
    
    # current date and time
    now = datetime.now(timezone.utc)

    # setting expiry time,issued at,token type in payload 
    payload.update({
        "exp": now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        "iat": now,
        "token_type": "access"
    })

    # generate access token
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token


def verify_token(token: str):
    payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=settings.ALGORITHM
        )
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=settings.ALGORITHM
        )
        return payload
    except JWTError:
        return None
    

from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
)


def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)