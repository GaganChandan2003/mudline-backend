#!/usr/bin/env python3
"""
Test script to check if all models can be imported and configured correctly
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from backend.database import engine, Base
    from backend.models import *
    
    print("✓ All models imported successfully")
    
    # Try to configure the registry
    from sqlalchemy.orm import configure_mappers
    configure_mappers()
    print("✓ All mappers configured successfully")
    
    # Try to create tables
    Base.metadata.create_all(bind=engine)
    print("✓ All tables created successfully")
    
    print("✅ All tests passed!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc() 