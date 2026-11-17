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

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Format: postgresql://<username>:<password>@<host>:<port>/<database_name>
DATABASE_URL = "postgresql://postgres:9884@localhost:5432/MilkDB"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Dependency to inject a DB session into FastAPI routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
