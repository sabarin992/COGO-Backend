from fastapi import FastAPI

from app.api.v1.router import api_router
from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost:5173"# React frontend
]


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router,prefix="/api/v1")


