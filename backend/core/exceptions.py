from fastapi import HTTPException, status


class MudlineXException(HTTPException):
    """Base exception for MudlineX application"""
    pass


class UserNotFoundException(MudlineXException):
    def __init__(self, user_id: str = None):
        detail = f"User not found" if user_id is None else f"User with id {user_id} not found"
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class TruckNotFoundException(MudlineXException):
    def __init__(self, truck_id: str = None):
        detail = f"Truck not found" if truck_id is None else f"Truck with id {truck_id} not found"
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class BookingNotFoundException(MudlineXException):
    def __init__(self, booking_id: str = None):
        detail = f"Booking not found" if booking_id is None else f"Booking with id {booking_id} not found"
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class MaterialNotFoundException(MudlineXException):
    def __init__(self, material_id: str = None):
        detail = f"Material not found" if material_id is None else f"Material with id {material_id} not found"
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class VehicleTypeNotFoundException(MudlineXException):
    def __init__(self, vehicle_type_id: str = None):
        detail = f"Vehicle type not found" if vehicle_type_id is None else f"Vehicle type with id {vehicle_type_id} not found"
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class LocationNotFoundException(MudlineXException):
    def __init__(self, location_id: str = None):
        detail = f"Location not found" if location_id is None else f"Location with id {location_id} not found"
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class TruckNotAvailableException(MudlineXException):
    def __init__(self, truck_id: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Truck {truck_id} is not available for booking"
        )


class BookingNotAllowedException(MudlineXException):
    def __init__(self, message: str):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=message)


class InsufficientCapacityException(MudlineXException):
    def __init__(self, truck_capacity: float, requested_quantity: float):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Truck capacity ({truck_capacity}) is insufficient for requested quantity ({requested_quantity})"
        )


class PaymentFailedException(MudlineXException):
    def __init__(self, message: str = "Payment processing failed"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=message)


class InvalidLocationException(MudlineXException):
    def __init__(self, message: str = "Invalid location provided"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=message)


class UnauthorizedAccessException(MudlineXException):
    def __init__(self, message: str = "Unauthorized access"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=message)


class ValidationException(MudlineXException):
    def __init__(self, message: str):
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=message) 