from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import require_roles
from app.db.session import get_db
from app.models.enums import Daypart, UserRole
from app.models.user import User
from app.schemas.dto import BreakRead, DeliveryRow, FillRow, RevenueReport
from app.services import breaks as break_service
from app.services import reports as report_service

router = APIRouter(tags=["reports"])
_any = require_roles(UserRole.ad_sales_executive, UserRole.traffic_manager, UserRole.ad_revenue_head)


@router.get("/availability", response_model=list[BreakRead])
def availability(
    channel_id: UUID | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    daypart: Daypart | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(_any),
) -> list[BreakRead]:
    return break_service.list_breaks(db, channel_id, date_from, date_to, daypart)


@router.get("/reports/fill", response_model=list[FillRow])
def fill_report(
    channel_id: UUID | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    daypart: Daypart | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(_any),
) -> list[FillRow]:
    return report_service.fill_report(db, channel_id, date_from, date_to, daypart)


@router.get("/reports/delivery", response_model=list[DeliveryRow])
def delivery_report(db: Session = Depends(get_db), _: User = Depends(_any)) -> list[DeliveryRow]:
    return report_service.delivery_report(db)


@router.get("/reports/revenue", response_model=RevenueReport)
def revenue_report(db: Session = Depends(get_db), _: User = Depends(_any)) -> RevenueReport:
    return report_service.revenue_report(db)
