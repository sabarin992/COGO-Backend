from jose import jwt,JWTError
from datetime import datetime,timedelta,timezone
from app.core.config import settings


def create_access_token(data: dict):
    payload = data.copy()

    if "sub" not in payload:
        raise ValueError("Token must contain 'sub'")

    now = datetime.now(timezone.utc)

    payload.update({
        "exp": now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        "iat": now,
        "token_type": "access"
    })

    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token