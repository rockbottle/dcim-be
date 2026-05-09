import os
from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# 1. Update the Connection URL
# SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL","postgresql://pguser:P%40ssw0rd@dcim-db:5432/dcim")
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
# 2. Create the Engine
# We remove connect_args={"check_same_thread": False} as it is SQLite-only
engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


# Base = declarative_base()
class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
