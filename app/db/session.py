from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


db_url = "postgresql+psycopg2://sabarinathem@localhost:5432/cogo"
engine = create_engine(db_url)
SessionLocal = sessionmaker(autoflush=False,autocommit=False,bind=engine)



