from app.database import engine, Base
from sqlalchemy import inspect

def check_tables():
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print("Tables in database:", tables)
    
    # Try to create tables if they don't exist
    if not tables:
        print("No tables found. Creating tables...")
        from app.models import user, profile, truck, booking, location, payment, rating, notification
        Base.metadata.create_all(bind=engine)
        print("Tables created successfully!")
        
        # Check tables again
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print("Tables after creation:", tables)
    else:
        print("Tables already exist.")

if __name__ == "__main__":
    check_tables()
