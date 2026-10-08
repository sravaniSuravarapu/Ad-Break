from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import require_roles
from app.db.session import get_db
from app.models.enums import Daypart, UserRole
from app.models.user import User
from app.schemas.dto import BreakCreate, BreakRead, BreakUpdate
from app.services import breaks as break_service

router = APIRouter(prefix="/breaks", tags=["breaks"])
_traffic = require_roles(UserRole.traffic_manager)
_any = require_roles(UserRole.ad_sales_executive, UserRole.traffic_manager, UserRole.ad_revenue_head)


@router.get("", response_model=list[BreakRead])
def list_breaks(
    channel_id: UUID | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    daypart: Daypart | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(_any),
) -> list[BreakRead]:
    return break_service.list_breaks(db, channel_id, date_from, date_to, daypart)


@router.post("", response_model=BreakRead, status_code=201)
def create_break(
    payload: BreakCreate,
    db: Session = Depends(get_db),
    user: User = Depends(_traffic),
) -> BreakRead:
    # BR-09: only a traffic manager creates breaks.
    return break_service.create_break(db, user, payload)


@router.patch("/{break_id}", response_model=BreakRead)
def update_break(
    break_id: UUID,
    payload: BreakUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(_traffic),
) -> BreakRead:
    return break_service.update_break(db, user, break_id, payload)
