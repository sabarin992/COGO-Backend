from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings


db_url = settings.DATABASE_URL
engine = create_engine(db_url)
SessionLocal = sessionmaker(autoflush=False,autocommit=False,bind=engine)





