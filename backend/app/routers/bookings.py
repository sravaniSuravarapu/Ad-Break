from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import require_roles
from app.db.session import get_db
from app.models.enums import BookingStatus, UserRole
from app.models.user import User
from app.schemas.dto import AsRunUpdate, BookingCreate, BookingMove, BookingRead, BookingRebook
from app.services import booking as booking_service

router = APIRouter(prefix="/bookings", tags=["bookings"])
_sales = require_roles(UserRole.ad_sales_executive)
_traffic = require_roles(UserRole.traffic_manager)
_any = require_roles(UserRole.ad_sales_executive, UserRole.traffic_manager, UserRole.ad_revenue_head)


@router.get("", response_model=list[BookingRead])
def list_bookings(
    campaign_id: UUID | None = None,
    ad_break_id: UUID | None = None,
    status: BookingStatus | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(_any),
) -> list[BookingRead]:
    return booking_service.list_bookings(db, campaign_id, ad_break_id, status)


@router.post("", response_model=BookingRead, status_code=201)
def create_booking(
    payload: BookingCreate,
    db: Session = Depends(get_db),
    user: User = Depends(_sales),
) -> BookingRead:
    return booking_service.create_booking(db, user, payload)


@router.post("/{booking_id}/cancel", response_model=BookingRead)
def cancel_booking(
    booking_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(_sales),
) -> BookingRead:
    return booking_service.cancel_booking(db, user, booking_id)


@router.post("/{booking_id}/move", response_model=BookingRead)
def move_booking(
    booking_id: UUID,
    payload: BookingMove,
    db: Session = Depends(get_db),
    user: User = Depends(_sales),
) -> BookingRead:
    return booking_service.move_booking(db, user, booking_id, payload)


@router.post("/{booking_id}/rebook", response_model=BookingRead, status_code=201)
def rebook_booking(
    booking_id: UUID,
    payload: BookingRebook,
    db: Session = Depends(get_db),
    user: User = Depends(_sales),
) -> BookingRead:
    return booking_service.rebook_booking(db, user, booking_id, payload)


@router.post("/{booking_id}/as-run", response_model=BookingRead)
def mark_as_run(
    booking_id: UUID,
    payload: AsRunUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(_traffic),
) -> BookingRead:
    # BR-09: only a traffic manager marks aired or missed.
    return booking_service.mark_as_run(db, user, booking_id, payload)
