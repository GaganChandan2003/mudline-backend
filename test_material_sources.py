#!/usr/bin/env python3
"""
Test script to check material sources functionality
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.database import get_db
from backend.models.material import MaterialSource, MaterialTypeModel
from sqlalchemy.orm import Session

def test_material_sources():
    """Test material sources query"""
    try:
        # Get database session
        db = next(get_db())
        
        # Test querying material types
        print("Testing material types query...")
        material_types = db.query(MaterialTypeModel).all()
        print(f"Found {len(material_types)} material types")
        for mt in material_types:
            print(f"  - {mt.type}: {mt.description}")
        
        # Test querying material sources
        print("\nTesting material sources query...")
        material_sources = db.query(MaterialSource).all()
        print(f"Found {len(material_sources)} material sources")
        for ms in material_sources[:3]:  # Show first 3
            print(f"  - {ms.source_name}: {ms.location}, {ms.city}, {ms.state}")
        
        print("\nTest completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_material_sources() 