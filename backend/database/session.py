from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATABASE_FILENAME = "financial_tracker.db"
DATABASE_PATH = PROJECT_ROOT / DATABASE_FILENAME

# Define the path to the SQLite database file
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# Create the SQLAlchemy engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Each instance of SessionLocal class is a new DB session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# This 'Base' will be used as a base class for DB models
Base = declarative_base()
