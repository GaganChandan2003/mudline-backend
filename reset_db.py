from backend.database import Base, engine
from backend.models import user, profile  # Import models to ensure they're registered with SQLAlchemy

print("Dropping all tables...")
Base.metadata.drop_all(bind=engine)

print("Creating all tables...")
Base.metadata.create_all(bind=engine)

print("Database reset complete!")
