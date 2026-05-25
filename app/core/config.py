from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OTP_EXPIRE_SECONDS: int = 60
    DATABASE_URL: str
    FRONTEND_ORIGIN:str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1
    APP_PASSWORD:str
    GOOGLE_CLIENT_ID:str

    class Config:
        env_file = ".env"

settings = Settings()

