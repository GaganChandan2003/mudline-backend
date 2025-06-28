"""
Database migration script to add new tables and update existing ones
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from backend.database import engine

def run_migrations():
    """Run database migrations"""
    with engine.connect() as conn:
        # Create materials table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS materials (
                id VARCHAR(36) PRIMARY KEY,
                type VARCHAR(10) NOT NULL,
                source VARCHAR(200) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """))
        
        # Create vehicle_types table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS vehicle_types (
                id VARCHAR(36) PRIMARY KEY,
                name VARCHAR(200) NOT NULL,
                capacity_ton DECIMAL(10,2) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """))
        
        # Update trucks table to match new schema
        conn.execute(text("""
            ALTER TABLE trucks 
            ADD COLUMN IF NOT EXISTS vehicle_number VARCHAR(20) UNIQUE,
            ADD COLUMN IF NOT EXISTS vehicle_type_id VARCHAR(36),
            ADD COLUMN IF NOT EXISTS driver_name VARCHAR(100),
            ADD COLUMN IF NOT EXISTS driver_contact VARCHAR(20),
            ADD COLUMN IF NOT EXISTS current_location VARCHAR(200),
            ADD COLUMN IF NOT EXISTS is_available BOOLEAN DEFAULT TRUE,
            ADD FOREIGN KEY IF NOT EXISTS (vehicle_type_id) REFERENCES vehicle_types(id)
        """))
        
        # Update bookings table to match new schema
        conn.execute(text("""
            ALTER TABLE bookings 
            ADD COLUMN IF NOT EXISTS user_id VARCHAR(36),
            ADD COLUMN IF NOT EXISTS material_id VARCHAR(36),
            ADD COLUMN IF NOT EXISTS source VARCHAR(200),
            ADD COLUMN IF NOT EXISTS destination VARCHAR(200),
            ADD COLUMN IF NOT EXISTS vehicle_type_id VARCHAR(36),
            ADD COLUMN IF NOT EXISTS assigned_truck_id VARCHAR(36),
            ADD COLUMN IF NOT EXISTS booking_time TIMESTAMP,
            ADD COLUMN IF NOT EXISTS expected_delivery_time TIMESTAMP,
            ADD COLUMN IF NOT EXISTS actual_delivery_time TIMESTAMP,
            ADD COLUMN IF NOT EXISTS state VARCHAR(20) DEFAULT 'Pending',
            ADD FOREIGN KEY IF NOT EXISTS (user_id) REFERENCES users(id),
            ADD FOREIGN KEY IF NOT EXISTS (material_id) REFERENCES materials(id),
            ADD FOREIGN KEY IF NOT EXISTS (vehicle_type_id) REFERENCES vehicle_types(id),
            ADD FOREIGN KEY IF NOT EXISTS (assigned_truck_id) REFERENCES trucks(id)
        """))
        
        # Create booking_status_history table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS booking_status_history (
                id VARCHAR(36) PRIMARY KEY,
                booking_id VARCHAR(36) NOT NULL,
                status VARCHAR(50) NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes TEXT,
                FOREIGN KEY (booking_id) REFERENCES bookings(id)
            )
        """))
        
        # Insert sample data
        insert_sample_data(conn)
        
        conn.commit()

def insert_sample_data(conn):
    """Insert sample data for testing"""
    # Insert sample materials
    conn.execute(text("""
        INSERT IGNORE INTO materials (id, type, source) VALUES
        ('550e8400-e29b-41d4-a716-446655440001', 'Sand', 'Dumka'),
        ('550e8400-e29b-41d4-a716-446655440002', 'Sand', 'Nawada'),
        ('550e8400-e29b-41d4-a716-446655440003', 'Stone', 'Dumka'),
        ('550e8400-e29b-41d4-a716-446655440004', 'Stone', 'Nawada')
    """))
    
    # Insert sample vehicle types
    conn.execute(text("""
        INSERT IGNORE INTO vehicle_types (id, name, capacity_ton) VALUES
        ('660e8400-e29b-41d4-a716-446655440001', '14 WHEELER - 30 TON', 30.00),
        ('660e8400-e29b-41d4-a716-446655440002', '12 WHEELER - 25 TON', 25.00),
        ('660e8400-e29b-41d4-a716-446655440003', '10 WHEELER - 20 TON', 20.00),
        ('660e8400-e29b-41d4-a716-446655440004', '8 WHEELER - 15 TON', 15.00)
    """))

if __name__ == "__main__":
    run_migrations()
    print("Migrations completed successfully!") 