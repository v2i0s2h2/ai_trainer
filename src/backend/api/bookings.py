"""
Booking API Routes
"""

from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.backend.database.db import get_db
from src.backend.database.models import Booking, User
from src.backend.auth.security import get_current_user as get_user_from_token

router = APIRouter(prefix="/api/bookings", tags=["bookings"])
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Dependency to get current authenticated user"""
    return get_user_from_token(credentials.credentials, db)


# Pydantic schemas
class BookingCreate(BaseModel):
    name: str
    day: str
    time: str
    booking_date: str  # ISO format: "2025-12-20"


class BookingResponse(BaseModel):
    id: int
    name: str
    day: str
    time: str
    booking_date: str
    status: str
    created_at: str
    
    class Config:
        from_attributes = True


@router.post("/", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
def create_booking(
    booking_data: BookingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new consultation booking"""
    
    # Parse booking date
    try:
        booking_datetime = datetime.fromisoformat(booking_data.booking_date)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use ISO format (YYYY-MM-DD)"
        )
    
    # Check if slot is already booked
    existing = db.query(Booking).filter(
        Booking.day == booking_data.day,
        Booking.time == booking_data.time,
        Booking.booking_date == booking_datetime,
        Booking.status == "confirmed"
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This time slot is already booked"
        )
    
    # Create booking
    new_booking = Booking(
        user_id=current_user.id,
        name=booking_data.name,
        day=booking_data.day,
        time=booking_data.time,
        booking_date=booking_datetime,
        status="confirmed"  # Auto-confirm
    )
    
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    
    return BookingResponse(
        id=new_booking.id,
        name=new_booking.name,
        day=new_booking.day,
        time=new_booking.time,
        booking_date=new_booking.booking_date.isoformat(),
        status=new_booking.status,
        created_at=new_booking.created_at.isoformat()
    )


@router.get("/my", response_model=List[BookingResponse])
def get_my_bookings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's bookings"""
    bookings = db.query(Booking).filter(
        Booking.user_id == current_user.id
    ).order_by(Booking.booking_date.desc()).all()
    
    return [
        BookingResponse(
            id=b.id,
            name=b.name,
            day=b.day,
            time=b.time,
            booking_date=b.booking_date.isoformat(),
            status=b.status,
            created_at=b.created_at.isoformat()
        )
        for b in bookings
    ]


@router.get("/", response_model=List[BookingResponse])
def get_all_bookings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all bookings (admin view vs public status)"""
    bookings = db.query(Booking).order_by(
        Booking.booking_date.desc()
    ).all()
    
    is_admin = current_user.role == "admin"
    
    return [
        BookingResponse(
            id=b.id,
            name=b.name if is_admin else "Booked", # Hide name for non-admins
            day=b.day,
            time=b.time,
            booking_date=b.booking_date.isoformat(),
            status=b.status,
            created_at=b.created_at.isoformat()
        )
        for b in bookings
    ]


@router.delete("/{booking_id}")
def cancel_booking(
    booking_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel a booking (only if >24 hours before appointment)"""
    
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    # Check ownership
    if booking.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only cancel your own bookings"
        )
    
    # Check if already cancelled
    if booking.status == "cancelled":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Booking is already cancelled"
        )
    
    # Check 24-hour rule
    time_until_booking = booking.booking_date - datetime.utcnow()
    if time_until_booking < timedelta(hours=24):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot cancel within 24 hours of appointment"
        )
    
    # Cancel booking
    booking.status = "cancelled"
    booking.cancelled_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Booking cancelled successfully"}
