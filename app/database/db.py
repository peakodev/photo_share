from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.conf.config import settings


engine = create_engine(settings.postgres_url())
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# D ependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
