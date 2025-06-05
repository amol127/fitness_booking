
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, EmailStr
from typing import List
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import  relationship

from app.database.db import Base, engine


class FitnessClass(Base):
    __tablename__ = "fitness_classes"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    date_time = Column(DateTime)
    instructor = Column(String)
    available_slots = Column(Integer)
    bookings = relationship("Booking", back_populates="fitness_class")


class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    client_name = Column(String)
    client_email = Column(String)
    class_id = Column(Integer, ForeignKey("fitness_classes.id"))
    fitness_class = relationship("FitnessClass", back_populates="bookings")


Base.metadata.create_all(bind=engine)
