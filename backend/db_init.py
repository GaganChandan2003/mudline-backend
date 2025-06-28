from backend.database import engine, Base
# Import models so that they are registered with SQLAlchemy metadata
from backend.models import (
    user,
    profile,
    truck,
    booking,
    location,
    payment,
    rating,
    notification,
)

# Create all tables
Base.metadata.create_all(bind=engine)
print("Database tables created successfully!")
