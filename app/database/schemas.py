from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from typing import Optional

class FitnessClassBase(BaseModel):
    name: str
    instructor: str
    available_slots: int

class FitnessClassCreate(FitnessClassBase):
    date_time: datetime

class FitnessClass(FitnessClassBase):
    id: int
    date_time: datetime
    model_config = ConfigDict(from_attributes=True)

class BookingBase(BaseModel):
    client_name: str
    client_email: EmailStr
    class_id: int

class BookingCreate(BookingBase):
    pass

class Booking(BookingBase):
    id: int
    fitness_class: FitnessClass
    model_config = ConfigDict(from_attributes=True)

class BookingResponse(BaseModel):
    id: int
    class_name: str
    instructor: str
    date_time: datetime
    client_name: str
    client_email: EmailStr
    model_config = ConfigDict(json_encoders={datetime: lambda v: v.strftime("%Y-%m-%dT%H:%M:%S%z")}) 