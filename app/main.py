from fastapi import FastAPI

from app.api.v1.router import api_router
from fastapi.middleware.cors import CORSMiddleware
from app.db.base import Base
from app.db.session import engine
from app.models.user import User
from app.models.kyc_docs import KYC
from app.core.config import settings



app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:3000",
        settings.FRONTEND_ORIGIN,
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


Base.metadata.create_all(engine)

app.include_router(api_router,prefix="/api/v1")


