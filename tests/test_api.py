import os
import sys
from pathlib import Path

# Add the project root directory to Python path
project_root = str(Path(__file__).parent.parent)
sys.path.insert(0, project_root)

from fastapi.testclient import TestClient
import pytest
from datetime import datetime, timedelta
import pytz
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database.db import Base, get_db
from app.models.models import FitnessClass, Booking

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

client = TestClient(app)

# ===== Classes Router Tests =====

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "msg" in data
    assert data["msg"] == "Welcome to Fitness Classes API!"

def test_get_classes_empty():
    """Test getting classes when no classes exist"""
    response = client.get("/fitness/classes")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0

def test_get_classes_with_data():
    """Test getting classes with sample data"""
    # Add a test class
    db = TestingSessionLocal()
    test_class = FitnessClass(
        name="Test Yoga",
        date_time=datetime.now(pytz.timezone('Asia/Kolkata')) + timedelta(days=1),
        instructor="Test Instructor",
        available_slots=5
    )
    db.add(test_class)
    db.commit()
    db.close()

    response = client.get("/fitness/classes")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["name"] == "Test Yoga"
    assert "date_time" in data[0]
    assert data[0]["instructor"] == "Test Instructor"
    assert data[0]["available_slots"] == 5

def test_get_classes_past_date():
    """Test getting classes with past date"""
    # Add a past class
    db = TestingSessionLocal()
    past_class = FitnessClass(
        name="Past Yoga",
        date_time=datetime.now(pytz.timezone('Asia/Kolkata')) - timedelta(days=1),
        instructor="Past Instructor",
        available_slots=5
    )
    db.add(past_class)
    db.commit()
    db.close()

    response = client.get("/fitness/classes")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0  # Past classes should not be returned

def test_get_classes_no_slots():
    """Test getting classes with no available slots"""
    # Add a class with no slots
    db = TestingSessionLocal()
    no_slots_class = FitnessClass(
        name="No Slots Yoga",
        date_time=datetime.now(pytz.timezone('Asia/Kolkata')) + timedelta(days=1),
        instructor="No Slots Instructor",
        available_slots=0
    )
    db.add(no_slots_class)
    db.commit()
    db.close()

    response = client.get("/fitness/classes")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0  # Classes with no slots should not be returned

# ===== Bookings Router Tests =====

def test_create_booking_success():
    """Test successful booking creation"""
    # First create a class
    db = TestingSessionLocal()
    test_class = FitnessClass(
        name="Test Yoga",
        date_time=datetime.now(pytz.timezone('Asia/Kolkata')) + timedelta(days=1),
        instructor="Test Instructor",
        available_slots=5
    )
    db.add(test_class)
    db.commit()
    db.close()

    # Create booking
    booking_data = {
        "class_id": 1,
        "client_name": "Test User",
        "client_email": "test@example.com"
    }
    response = client.post("/fitness/book", json=booking_data)
    assert response.status_code == 200
    data = response.json()
    assert data["class_name"] == "Test Yoga"
    assert data["client_name"] == "Test User"
    assert data["client_email"] == "test@example.com"

def test_create_booking_invalid_class():
    """Test booking with invalid class ID"""
    booking_data = {
        "class_id": 999,
        "client_name": "Test User",
        "client_email": "test@example.com"
    }
    response = client.post("/fitness/book", json=booking_data)
    assert response.status_code == 404
    assert "Fitness class not found" in response.json()["detail"]

def test_create_booking_no_slots():
    """Test booking when no slots are available"""
    # Create a class with no slots
    db = TestingSessionLocal()
    no_slots_class = FitnessClass(
        name="No Slots Yoga",
        date_time=datetime.now(pytz.timezone('Asia/Kolkata')) + timedelta(days=1),
        instructor="No Slots Instructor",
        available_slots=0
    )
    db.add(no_slots_class)
    db.commit()
    db.close()

    booking_data = {
        "class_id": 1,
        "client_name": "Test User",
        "client_email": "test@example.com"
    }
    response = client.post("/fitness/book", json=booking_data)
    assert response.status_code == 400
    assert "No available slots" in response.json()["detail"]

def test_create_booking_duplicate():
    """Test duplicate booking attempt"""
    # First create a class
    db = TestingSessionLocal()
    test_class = FitnessClass(
        name="Test Yoga",
        date_time=datetime.now(pytz.timezone('Asia/Kolkata')) + timedelta(days=1),
        instructor="Test Instructor",
        available_slots=5
    )
    db.add(test_class)
    db.commit()
    db.close()

    # Create first booking
    booking_data = {
        "class_id": 1,
        "client_name": "Test User",
        "client_email": "test@example.com"
    }
    response = client.post("/fitness/book", json=booking_data)
    assert response.status_code == 200

    # Try to create duplicate booking
    response = client.post("/fitness/book", json=booking_data)
    assert response.status_code == 400
    assert "Already Booked" in response.json()["detail"]

def test_get_bookings_success():
    """Test getting bookings by email"""
    # First create a class and booking
    db = TestingSessionLocal()
    test_class = FitnessClass(
        name="Test Yoga",
        date_time=datetime.now(pytz.timezone('Asia/Kolkata')) + timedelta(days=1),
        instructor="Test Instructor",
        available_slots=5
    )
    db.add(test_class)
    db.commit()
    
    test_booking = Booking(
        client_name="Test User",
        client_email="test@example.com",
        class_id=1
    )
    db.add(test_booking)
    db.commit()
    db.close()

    # Get bookings
    response = client.get("/fitness/bookings?email=test@example.com")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["class_name"] == "Test Yoga"
    assert data[0]["client_name"] == "Test User"
    assert data[0]["client_email"] == "test@example.com"

def test_get_bookings_no_results():
    """Test getting bookings with no results"""
    response = client.get("/fitness/bookings?email=nonexistent@example.com")
    assert response.status_code == 404
    assert "No bookings found" in response.json()["detail"]

# def test_get_bookings_invalid_email():
#     """Test getting bookings with invalid email format"""
#     response = client.get("/fitness/bookings?email=invalid-email")
#     assert response.status_code == 422
#     assert "email" in str(response.json()["detail"]).lower()


def test_create_booking_invalid_email():
    """Test creating booking with invalid email format"""
    # First create a class
    db = TestingSessionLocal()
    test_class = FitnessClass(
        name="Test Yoga",
        date_time=datetime.now(pytz.timezone('Asia/Kolkata')) + timedelta(days=1),
        instructor="Test Instructor",
        available_slots=5
    )
    db.add(test_class)
    db.commit()
    db.close()

    booking_data = {
        "class_id": 1,
        "client_name": "Test User",
        "client_email": "invalid-email"
    }
    response = client.post("/fitness/book", json=booking_data)
    assert response.status_code == 422
    assert "email" in str(response.json()["detail"]).lower()


def test_create_booking_missing_fields():
    """Test creating booking with missing required fields"""
    booking_data = {
        "class_id": 1,
        "client_name": "Test User"
        # Missing client_email
    }
    response = client.post("/fitness/book", json=booking_data)
    assert response.status_code == 422
    assert "client_email" in response.json()["detail"][0]["loc"] 