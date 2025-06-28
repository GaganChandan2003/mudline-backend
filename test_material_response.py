#!/usr/bin/env python3
"""
Test script to check MaterialSourceResponse serialization
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.database import get_db
from backend.models.material import MaterialSource, MaterialTypeModel
from backend.schemas.material import MaterialSourceResponse
from sqlalchemy.orm import Session, joinedload

def test_material_source_response():
    """Test MaterialSourceResponse serialization"""
    try:
        # Get database session
        db = next(get_db())
        
        # Test querying material sources with joinedload
        print("Testing material sources query with joinedload...")
        material_sources = db.query(MaterialSource).options(joinedload(MaterialSource.material_type)).all()
        print(f"Found {len(material_sources)} material sources")
        
        # Test serialization of first material source
        if material_sources:
            ms = material_sources[0]
            print(f"\nTesting serialization of: {ms.source_name}")
            print(f"Material type: {ms.material_type.type if ms.material_type else 'None'}")
            
            try:
                response = MaterialSourceResponse.model_validate(ms, from_attributes=True)
                print("Serialization successful!")
                print(f"Response ID: {response.id}")
                print(f"Material type ID: {response.material_type.id}")
                print(f"Material type: {response.material_type.type}")
            except Exception as e:
                print(f"Serialization failed: {e}")
                import traceback
                traceback.print_exc()
        
        print("\nTest completed!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_material_source_response() 