import uuid

def uuid_to_str(obj):
    if isinstance(obj, dict):
        return {k: uuid_to_str(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [uuid_to_str(i) for i in obj]
    elif isinstance(obj, uuid.UUID):
        return str(obj)
    elif hasattr(obj, "__dict__"):
        # Handle SQLAlchemy objects
        result = {}
        for key, value in vars(obj).items():
            if key.startswith('_'):
                continue  # Skip SQLAlchemy internal attributes
            if hasattr(value, 'value') and hasattr(value, '__class__') and 'Enum' in str(value.__class__):
                # Handle SQLAlchemy Enum fields
                result[key] = value.value
            elif hasattr(value, 'name') and hasattr(value, 'value') and hasattr(value, '__class__') and 'enum' in str(value.__class__).lower():
                # Handle Python Enum objects
                result[key] = value.value
            else:
                result[key] = uuid_to_str(value)
        return result
    return obj 