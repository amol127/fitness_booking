

from fastapi import FastAPI
from datetime import datetime
import logging
import pytz
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy.exc import SQLAlchemyError

from app.database.db import SessionLocal
from app.models.models import FitnessClass
from app.routers import classes, bookings


# === LOGGING CONFIG == 
IST = pytz.timezone('Asia/Kolkata')
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
# === END LOGGING CONFIG ==


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle manager to seed sample data and log startup/shutdown events.
    """
    logger.info("Starting up Fitness Studio Booking API")

    db = SessionLocal()
    try:
        # Seed sample data if no classes exist
        existing_classes = db.query(FitnessClass).first()
        if not existing_classes:
            logger.info("No existing classes found, seeding sample data")
            sample_classes = [
                FitnessClass(
                    name="Yoga",
                    date_time=pytz.timezone('Asia/Kolkata').localize(datetime(2025, 6, 10, 8, 0)),
                    instructor="Asha",
                    available_slots=5
                ),
                FitnessClass(
                    name="Zumba",
                    date_time=pytz.timezone('Asia/Kolkata').localize(datetime(2025, 6, 11, 10, 0)),
                    instructor="Raj",
                    available_slots=10
                ),
                FitnessClass(
                    name="HIIT",
                    date_time=pytz.timezone('Asia/Kolkata').localize(datetime(2025, 6, 12, 18, 0)),
                    instructor="Meera",
                    available_slots=7
                )
            ]
            try:
                db.add_all(sample_classes)
                db.commit()
                logger.info("Sample classes added successfully.")
            except SQLAlchemyError as e:
                db.rollback()
                logger.error(f"Database error while seeding classes: {str(e)}")
                raise
    except Exception as e:
        logger.error(f"Unexpected startup error: {str(e)}")
        raise
    finally:
        db.close()

    yield  # Application runs here

    # Shutdown
    logger.info("Shutting down Fitness Studio Booking API")


# === Create FastAPI App ===
app = FastAPI(title="Fitness Studio Booking API", lifespan=lifespan)

# === CORS Middleware ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Include Routers ===
app.include_router(classes.router, prefix="/fitness")
app.include_router(bookings.router, prefix="/fitness")

# === Root Endpoint ===
@app.get("/", status_code=200)
async def start_project():
    logger.info("Root endpoint accessed")
    return {"msg": "Welcome to Fitness Classes API!"}
