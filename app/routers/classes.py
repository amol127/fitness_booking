from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from app.database.db import get_db
from app.models.models import FitnessClass

# Logger setup
logger = logging.getLogger(__name__)

router = APIRouter(tags=["classes"])


@router.get("/classes")
async def get_classes(db: Session = Depends(get_db)):
    """
    Get all upcoming fitness classes with available slots.
    """
    try:
        current_time = datetime.now()

        classes = (
            db.query(FitnessClass)
            .filter(
                FitnessClass.date_time >= current_time,
                FitnessClass.available_slots > 0
            )
            .all()
        )

        if not classes:
            logger.info("No upcoming classes with available slots found.")
            raise HTTPException(status_code=404, detail="No upcoming classes found.")

        logger.info(f"Fetched {len(classes)} upcoming classes with available slots.")
        return [
            {
                "name": cls.name,
                "date_time": cls.date_time.strftime("%Y-%m-%d %I:%M:%S %p"),
                "instructor": cls.instructor,
                "available_slots": cls.available_slots
            }
            for cls in classes
        ]

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error while fetching classes: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
