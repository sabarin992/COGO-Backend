from fastapi import FastAPI

from app.api.v1.router import api_router
from fastapi.middleware.cors import CORSMiddleware
from app.db.base import Base
from app.db.session import engine
from app.models.user import User

origins = [
    "http://localhost:5173"
]


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


Base.metadata.create_all(engine)

app.include_router(api_router,prefix="/api/v1")


