from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
import logging

from app.database.db import get_db
from app.database.schemas import BookingCreate, BookingResponse
from app.models.models import Booking as BookingModel, FitnessClass

# Logger setup
logger = logging.getLogger(__name__)

router = APIRouter(tags=["bookings"])


@router.post("/book", response_model=BookingResponse)
async def create_booking(
    booking: BookingCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new booking for a fitness class.
    """
    try:
        fitness_class = db.query(FitnessClass).filter(FitnessClass.id == booking.class_id).first()
        if not fitness_class:
            logger.warning(f"Booking failed: Fitness class {booking.class_id} not found.")
            raise HTTPException(status_code=404, detail="Fitness class not found")
        
        if fitness_class.available_slots <= 0:
            logger.info(f"No slots available for class ID {booking.class_id}")
            raise HTTPException(status_code=400, detail="No available slots for this class")

        existing_email = db.query(BookingModel).filter(
            BookingModel.client_email == booking.client_email,
            BookingModel.class_id == booking.class_id
        ).first()
        if existing_email:
            logger.info(f"Duplicate booking attempt by {booking.client_email} for class ID {booking.class_id}")
            raise HTTPException(status_code=400, detail="You are already booked!")

        db_booking = BookingModel(
            client_name=booking.client_name,
            client_email=booking.client_email,
            class_id=booking.class_id
        )

        fitness_class.available_slots -= 1

        db.add(db_booking)
        db.commit()
        db.refresh(db_booking)

        logger.info(f"Booking successful: {booking.client_email} for class ID {booking.class_id}")

        return BookingResponse(
            id=db_booking.id,
            class_name=fitness_class.name,
            instructor=fitness_class.instructor,
            date_time=fitness_class.date_time,
            client_name=db_booking.client_name,
            client_email=db_booking.client_email
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Internal error during booking: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/bookings")
async def get_bookings_by_email(
    email: Optional[str] = Query(None, description="Email to fetch bookings for"),
    db: Session = Depends(get_db)
):
    """
    Get all bookings, or filter by email if provided.
    """
    try:
        query = db.query(BookingModel)

        if email:
            query = query.filter(BookingModel.client_email == email)

        bookings = query.all()

        if not bookings:
            logger.info(f"No bookings found for email: {email}")
            raise HTTPException(status_code=404, detail="No bookings found")

        result = []
        for booking in bookings:
            fitness_class = db.query(FitnessClass).filter(FitnessClass.id == booking.class_id).first()
            result.append({
                "class_name": fitness_class.name,
                "instructor": fitness_class.instructor,
                "date_time": fitness_class.date_time.strftime("%Y-%m-%d %I:%M:%S %p"),
                "client_name": booking.client_name,
                "client_email": booking.client_email,
            })

        logger.info(f"Returned {len(result)} bookings for email: {email if email else 'ALL'}")
        return result

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error fetching bookings: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
