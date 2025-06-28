#!/usr/bin/env python3
"""
Test script to debug enum conversion
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.database import get_db
from backend.models.material import MaterialTypeModel
from backend.utils.uuid_to_str import uuid_to_str
from backend.schemas.material import MaterialTypeResponse

def test_enum_conversion():
    """Test enum conversion"""
    try:
        # Get database session
        db = next(get_db())
        
        # Get first material type
        material_type = db.query(MaterialTypeModel).first()
        print(f"Original material type: {material_type.type}")
        print(f"Type of material_type.type: {type(material_type.type)}")
        
        # Convert using uuid_to_str
        converted = uuid_to_str(material_type)
        print(f"Converted dict: {converted}")
        print(f"Type field value: {converted.get('type')}")
        print(f"Type of type field: {type(converted.get('type'))}")
        
        # Try to validate with Pydantic
        try:
            response = MaterialTypeResponse.model_validate(converted)
            print("✅ Pydantic validation successful!")
            print(f"Response: {response.model_dump()}")
        except Exception as e:
            print(f"❌ Pydantic validation failed: {e}")
            import traceback
            traceback.print_exc()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_enum_conversion() 