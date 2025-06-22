from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy import URL
from config import config

print(f"Connecting to database: {config.DATABASE_URL.split('@')[1] if '@' in config.DATABASE_URL else config.DATABASE_URL}")

# Special handling for SQLite
if config.DATABASE_URL.startswith("sqlite"):
    # The 'check_same_thread' argument is needed for SQLite to work with FastAPI
    engine = create_engine(config.DATABASE_URL, echo=True, connect_args={"check_same_thread": False})
else:
    # Standard engine creation for PostgreSQL or other databases
    engine = create_engine(config.DATABASE_URL, echo=True)

def create_db_and_tables():
    """Create database tables"""
    SQLModel.metadata.create_all(engine)

def get_db_session():
    """Get database session"""
    with Session(engine) as session:
        yield session

def init_db():
    """Initialize database with tables"""
    create_db_and_tables() 