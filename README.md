# Fitness Studio Booking API

A FastAPI-based booking system for a fitness studio that manages class bookings, instructor schedules, and client reservations.

## Features

- View available fitness classes with real-time slot availability
- Book classes with automatic slot management
- View booking history by email
- Timezone-aware scheduling (IST)
- Input validation and error handling
- SQLite database with SQLAlchemy ORM
- Comprehensive test coverage

## Tech Stack

- Python 3.8+
- FastAPI (Web Framework)
- SQLAlchemy (ORM)
- Pydantic (Data Validation)
- SQLite (Database)
- Pytest (Testing)
- Uvicorn (ASGI Server)

## Project Structure

```
fitness_booking/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application setup
│   ├── models/
│   │   └── models.py        # SQLAlchemy models
│   ├── database/
│   │   ├── db.py           # Database configuration
│   │   └── schemas.py      # Pydantic schemas
│   └── routers/
│       ├── classes.py      # Class management endpoints
│       └── bookings.py     # Booking management endpoints
├── tests/
│   └── test_api.py         # API test cases
├── requirements.txt
└── README.md
```

## Setup Instructions

1. Clone the repository:
```bash
git clone <repository-url>
cd fitness_booking
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python run.py
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Available Endpoints

1. **GET /fitness/classes**
   - Returns list of all upcoming fitness classes
   - Query Parameters:
     - `date` (optional): Filter by date (YYYY-MM-DD)
     - `instructor` (optional): Filter by instructor name
   - Response:
     ```json
     [
       {
         "id": 1,
         "name": "Yoga",
         "instructor": "Asha",
         "date_time": "2025-06-06T08:00:00+05:30",
         "available_slots": 5
       }
     ]
     ```

2. **POST /fitness/book**
   - Book a class
   - Request Body:
     ```json
     {
         "class_id": 1,
         "client_name": "John Doe",
         "client_email": "john@example.com"
     }
     ```
   - Response:
     ```json
     {
         "id": 1,
         "class_name": "Yoga",
         "instructor": "Asha",
         "date_time": "2025-06-06T08:00:00+05:30",
         "client_name": "John Doe",
         "client_email": "john@example.com"
     }
     ```

3. **GET /fitness/bookings**
   - Get bookings by email
   - Query Parameters:
     - `email` (required): Filter bookings by email
   - Response:
     ```json
     [
       {
         "class_name": "Yoga",
         "instructor": "Asha",
         "date_time": "2025-06-06T08:00:00+05:30",
         "client_name": "John Doe",
         "client_email": "john@example.com"
       }
     ]
     ```

## Sample cURL Requests

1. Get all classes:
```bash
curl -X GET "http://localhost:8000/fitness/classes"
```

2. Book a class:
```bash
curl -X POST "http://localhost:8000/fitness/book" \
     -H "Content-Type: application/json" \
     -d '{"class_id": 1, "client_name": "John Doe", "client_email": "john@example.com"}'
```

3. Get bookings by email:
```bash
curl -X GET "http://localhost:8000/fitness/bookings?email=john@example.com"
```

## Testing

Run tests using pytest:
```bash
pytest
```

The test suite includes:
- Endpoint functionality tests
- Input validation tests
- Error handling tests
- Timezone handling tests
- Database operation tests

## Error Handling

The API implements comprehensive error handling for:
- Invalid input data (422 Unprocessable Entity)
- Overbooking attempts (400 Bad Request)
- Non-existent classes (404 Not Found)
- Duplicate bookings (400 Bad Request)
- Missing required fields (422 Unprocessable Entity)
- Database errors (500 Internal Server Error)

## Timezone Management

- All class times are stored and returned in IST (Indian Standard Time)
- API responses include timezone information (+05:30)
- Date-time validation ensures future dates only
- Proper timezone conversion for all datetime operations

## Database

- Uses SQLite with SQLAlchemy ORM
- Automatic database creation and migrations
- Sample data seeding on startup
- Proper connection management
- Transaction support for booking operations

## Security Features

- Input validation using Pydantic
- SQL injection prevention through SQLAlchemy
- CORS middleware for cross-origin requests
- Error handling to prevent information leakage
- Email format validation
- Data sanitization