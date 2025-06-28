from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from backend.config import settings

# MySQL engine configuration
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Enable connection health checks
    pool_recycle=3600,    # Recycle connections after 1 hour
    pool_size=5,          # Number of connections to keep open
    max_overflow=10,      # Number of connections to allow in overflow
    echo=False            # Set to True for SQL query logging
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency generator that provides a database session and ensures it is closed."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()