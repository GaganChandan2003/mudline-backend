# Material Transportation Booking System

A complete backend system for managing material transportation bookings (sand/stone) with automatic truck assignment and delivery tracking.

## 🎯 Features

- **Customer Booking Management**: Customers can create bookings for material transportation
- **Automatic Truck Assignment**: System automatically assigns the best available truck based on location and availability
- **Delivery Status Tracking**: Complete tracking of booking status from creation to delivery
- **Booking History**: Full history of all booking status changes
- **Truck Owner Management**: Truck owners can manage their fleet and view assigned bookings
- **Material & Vehicle Type Management**: Admin can manage different materials and vehicle types

## 📦 Database Models

### 1. Material
```sql
- id: UUID (Primary Key)
- type: ENUM("Sand", "Stone")
- source: VARCHAR(200) // eg: "Dumka", "Nawada"
- created_at: TIMESTAMP
- updated_at: TIMESTAMP
```

### 2. VehicleType
```sql
- id: UUID (Primary Key)
- name: VARCHAR(200) // eg: "14 WHEELER - 30 TON"
- capacity_ton: DECIMAL(10,2)
- created_at: TIMESTAMP
- updated_at: TIMESTAMP
```

### 3. Truck
```sql
- id: UUID (Primary Key)
- vehicle_number: VARCHAR(20) UNIQUE
- vehicle_type_id: UUID (FK -> VehicleType)
- truck_owner_id: UUID (FK -> User)
- driver_name: VARCHAR(100)
- driver_contact: VARCHAR(20)
- current_location: VARCHAR(200) // eg: district
- is_available: BOOLEAN
- latitude: DECIMAL(10,8)
- longitude: DECIMAL(11,8)
- status: ENUM("available", "booked", "in_transit", "maintenance")
- created_at: TIMESTAMP
- updated_at: TIMESTAMP
```

### 4. Booking
```sql
- id: UUID (Primary Key)
- user_id: UUID (FK -> User)
- material_id: UUID (FK -> Material)
- source: VARCHAR(200)
- destination: VARCHAR(200)
- vehicle_type_id: UUID (FK -> VehicleType)
- quantity: DECIMAL(10,2)
- status: ENUM("Pending", "Accepted", "Truck Assigned", "Loading", "In Transit", "Completed", "Cancelled")
- assigned_truck_id: UUID (FK -> Truck) - Optional
- booking_time: TIMESTAMP
- expected_delivery_time: TIMESTAMP - Optional
- actual_delivery_time: TIMESTAMP - Optional
- state: ENUM("Pending", "Accepted", "Assigned", "Loading", "Transit", "Delivered")
- created_at: TIMESTAMP
- updated_at: TIMESTAMP
```

### 5. BookingStatusHistory
```sql
- id: UUID (Primary Key)
- booking_id: UUID (FK -> Booking)
- status: VARCHAR(50)
- updated_at: TIMESTAMP
- notes: TEXT - Optional
```

## 🔄 Booking Flow

### 1. Customer Creates Booking
- **Endpoint**: `POST /api/v1/bookings/`
- **Input**: material_id, source, destination, vehicle_type_id, quantity, booking_time
- **Status**: Set to "Pending"
- **Process**: 
  - Validates material and vehicle type exist
  - Creates booking record
  - Triggers automatic truck assignment

### 2. Automatic Truck Assignment
- **Criteria**:
  - `is_available = true`
  - `vehicle_type_id` matches booking requirement
  - `current_location` matches or is near booking source
- **Process**:
  - Finds available trucks matching criteria
  - Selects best truck (currently first available, can be enhanced)
  - Updates booking with assigned truck
  - Sets status to "Truck Assigned"
  - Marks truck as unavailable
  - Adds status history entry

### 3. Status Updates
- **Endpoint**: `PATCH /api/v1/bookings/{id}/status`
- **Allowed Statuses**: Pending → Accepted → Truck Assigned → Loading → In Transit → Completed
- **Process**:
  - Updates booking status and state
  - Logs change in BookingStatusHistory
  - Handles truck availability (frees truck on completion/cancellation)

## ✅ API Endpoints

### Bookings
- `POST /api/v1/bookings/` - Create new booking
- `GET /api/v1/bookings/` - List all bookings (with optional status filter)
- `GET /api/v1/bookings/{id}` - Get booking details with all related data
- `GET /api/v1/bookings/{id}/status-history` - Get booking status history
- `PATCH /api/v1/bookings/{id}/assign-truck` - Assign truck to booking
- `PATCH /api/v1/bookings/{id}/status` - Update booking status
- `DELETE /api/v1/bookings/{id}` - Cancel booking

### Materials
- `GET /api/v1/materials/` - List all materials
- `GET /api/v1/materials/{id}` - Get material details
- `POST /api/v1/materials/` - Create new material (Admin only)
- `PUT /api/v1/materials/{id}` - Update material (Admin only)
- `DELETE /api/v1/materials/{id}` - Delete material (Admin only)

### Vehicle Types
- `GET /api/v1/vehicle-types/` - List all vehicle types
- `GET /api/v1/vehicle-types/{id}` - Get vehicle type details
- `POST /api/v1/vehicle-types/` - Create new vehicle type (Admin only)
- `PUT /api/v1/vehicle-types/{id}` - Update vehicle type (Admin only)
- `DELETE /api/v1/vehicle-types/{id}` - Delete vehicle type (Admin only)

### Trucks
- `GET /api/v1/trucks/` - List all trucks (Admin only)
- `GET /api/v1/trucks/{id}` - Get truck details
- `GET /api/v1/trucks/owner/{truck_owner_id}` - Get trucks under an owner
- `POST /api/v1/trucks/` - Create new truck (Truck Owner only)
- `PUT /api/v1/trucks/{id}` - Update truck
- `DELETE /api/v1/trucks/{id}` - Delete truck

## 🚀 Setup & Installation

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Database Migrations
```bash
python backend/migrations.py
```

### 3. Start the Server
```bash
python backend/main.py
```

### 4. Access API Documentation
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 📝 Sample API Usage

### Create a Booking
```bash
curl -X POST "http://localhost:8000/api/v1/bookings/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "material_id": "550e8400-e29b-41d4-a716-446655440001",
    "source": "Dumka",
    "destination": "Patna",
    "vehicle_type_id": "660e8400-e29b-41d4-a716-446655440001",
    "quantity": 25.5,
    "booking_time": "2024-01-15T10:00:00Z"
  }'
```

### Get Booking Details
```bash
curl -X GET "http://localhost:8000/api/v1/bookings/{booking_id}" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Update Booking Status
```bash
curl -X PATCH "http://localhost:8000/api/v1/bookings/{booking_id}/status" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "status": "In Transit",
    "state": "Transit",
    "expected_delivery_time": "2024-01-16T14:00:00Z"
  }'
```

## 🔧 Configuration

The system uses environment variables for configuration. Create a `.env` file based on `env.example`:

```env
DATABASE_URL=mysql://user:password@localhost/mudlinex
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_ORIGINS=["http://localhost:3000"]
```

## 🧪 Testing

The system includes sample data for testing:
- **Materials**: Sand (Dumka, Nawada), Stone (Dumka, Nawada)
- **Vehicle Types**: 14 Wheeler (30 ton), 12 Wheeler (25 ton), 10 Wheeler (20 ton), 8 Wheeler (15 ton)

## 🔒 Security

- JWT-based authentication
- Role-based access control (Customer, Truck Owner, Admin)
- Input validation using Pydantic schemas
- SQL injection protection through SQLAlchemy ORM

## 📊 Business Logic

### Truck Assignment Algorithm
1. **Filter by Availability**: Only available trucks
2. **Filter by Vehicle Type**: Match required capacity
3. **Filter by Location**: Trucks near source location
4. **Selection**: Currently selects first available (can be enhanced with:
   - Least used truck
   - Same owner preference
   - Driver rating
   - Truck condition

### Status Management
- **Pending**: Initial booking state
- **Accepted**: Booking confirmed
- **Truck Assigned**: Truck allocated
- **Loading**: Material being loaded
- **In Transit**: On the way to destination
- **Completed**: Successfully delivered
- **Cancelled**: Booking cancelled

## 🔄 Future Enhancements

1. **Advanced Truck Selection**: Implement sophisticated truck selection algorithm
2. **Real-time Tracking**: GPS tracking integration
3. **Payment Integration**: Payment processing for bookings
4. **Notifications**: Real-time status updates via SMS/Email
5. **Analytics**: Booking analytics and reporting
6. **Mobile App**: Native mobile applications
7. **Scheduling**: Advanced delivery scheduling
8. **Rating System**: Customer and driver rating system

## 📞 Support

For questions or issues, please refer to the API documentation or contact the development team. 