from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.conf.config import settings


engine = create_engine(settings.postgres_url())
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    # except Exception as err:
    #     print("get_db !!!!!!!!!!!!!!!!!!")
    #     raise err
    finally:
        db.close()
