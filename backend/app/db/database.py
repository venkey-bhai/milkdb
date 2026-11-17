# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker, declarative_base
# import pyodbc

# # DATABASE_URL = "sqlite:///./milk.db"

# DATABASE_URL = "mssql+pyodbc://@DESKTOP-S5IU22L\\SQLEXPRESS/MilkDB?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server"

# engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# SessionLocal   = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# Base = declarative_base()

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Get the connection string from Render environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is missing")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args={"sslmode": "require"}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


# Dependency to inject a DB session into FastAPI routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
