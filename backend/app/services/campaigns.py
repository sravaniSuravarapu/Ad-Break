from collections import defaultdict
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.clock import utc_now
from app.core.errors import NotFound, RuleError
from app.models.advertiser import Advertiser
from app.models.agency import Agency
from app.models.booking import Booking
from app.models.campaign import Campaign
from app.models.enums import ALLOWED_SPOT_LENGTHS, COMMITTED, BookingStatus, CampaignStatus
from app.models.user import User
from app.schemas.dto import (
    CampaignCreate,
    CampaignRead,
    CampaignStatusUpdate,
    CampaignUpdate,
)

_TRANSITIONS: dict[CampaignStatus, set[CampaignStatus]] = {
    CampaignStatus.draft: {CampaignStatus.active, CampaignStatus.cancelled},
    CampaignStatus.active: {CampaignStatus.completed, CampaignStatus.cancelled},
    CampaignStatus.completed: set(),
    CampaignStatus.cancelled: set(),
}


def _pct(part: Decimal | int, whole: Decimal | int) -> float:
    if not whole:
        return 0.0
    return round(float(part) / float(whole) * 100, 2)


def _metrics(bookings: list[Booking], planned: int, budget: Decimal) -> dict[str, int | Decimal | float]:
    spots_booked = sum(1 for row in bookings if row.status == BookingStatus.booked)
    spots_aired = sum(1 for row in bookings if row.status == BookingStatus.aired)
    spots_missed = sum(1 for row in bookings if row.status == BookingStatus.missed)
    counting = [row for row in bookings if row.status in COMMITTED]
    spent = sum((row.cost for row in counting), Decimal("0.00"))
    return {
        "spots_booked": spots_booked,
        "spots_aired": spots_aired,
        "spots_missed": spots_missed,
        "spots_counting": len(counting),
        "booked_cost": spent,
        "delivery_pct": _pct(spots_aired, planned),
        "budget_utilisation_pct": _pct(spent, budget),
    }


def _to_read(campaign: Campaign, advertiser_name: str, bookings: list[Booking]) -> CampaignRead:
    metrics = _metrics(bookings, campaign.planned_spots, campaign.budget)
    return CampaignRead(
        id=campaign.id,
        advertiser_id=campaign.advertiser_id,
        advertiser_name=advertiser_name,
        agency_id=campaign.agency_id,
        name=campaign.name,
        start_date=campaign.start_date,
        end_date=campaign.end_date,
        spot_length=campaign.spot_length,
        planned_spots=campaign.planned_spots,
        budget=campaign.budget,
        status=campaign.status,
        created_at=campaign.created_at,
        **metrics,  # type: ignore[arg-type]
    )


def _load(db: Session) -> list[CampaignRead]:
    campaigns = db.scalars(select(Campaign).order_by(Campaign.created_at.desc())).all()
    if not campaigns:
        return []
    advertisers = {
        row.id: row.name
        for row in db.scalars(
            select(Advertiser).where(Advertiser.id.in_([item.advertiser_id for item in campaigns]))
        ).all()
    }
    grouped: dict[UUID, list[Booking]] = defaultdict(list)
    for booking in db.scalars(
        select(Booking).where(Booking.campaign_id.in_([item.id for item in campaigns]))
    ).all():
        grouped[booking.campaign_id].append(booking)
    return [
        _to_read(campaign, advertisers.get(campaign.advertiser_id, ""), grouped[campaign.id])
        for campaign in campaigns
    ]


def list_campaigns(db: Session) -> list[CampaignRead]:
    return _load(db)


def get_campaign(db: Session, campaign_id: UUID) -> CampaignRead:
    for row in _load(db):
        if row.id == campaign_id:
            return row
    raise NotFound("Campaign not found.")


def _check_dates_and_length(start: object, end: object, spot_length: int) -> None:
    # BR-01
    if end < start:  # type: ignore[operator]
        raise RuleError("Campaign end date must be on or after the start date.", "BR-01")
    if spot_length not in ALLOWED_SPOT_LENGTHS:
        raise RuleError("Spot length must be one of 10, 15, 20, 30, 60 seconds.", "BR-01")


def create_campaign(db: Session, user: User, payload: CampaignCreate) -> CampaignRead:
    _check_dates_and_length(payload.start_date, payload.end_date, payload.spot_length)
    if db.get(Advertiser, payload.advertiser_id) is None:
        raise NotFound("Advertiser not found.")
    if payload.agency_id is not None and db.get(Agency, payload.agency_id) is None:
        raise NotFound("Agency not found.")
    now = utc_now()
    row = Campaign(
        advertiser_id=payload.advertiser_id,
        agency_id=payload.agency_id,
        name=payload.name,
        start_date=payload.start_date,
        end_date=payload.end_date,
        spot_length=payload.spot_length,
        planned_spots=payload.planned_spots,
        budget=payload.budget,
        status=CampaignStatus.draft,
        created_by=user.id,
        changed_by=user.id,
        created_at=now,
        updated_at=now,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return get_campaign(db, row.id)


def update_campaign(
    db: Session, user: User, campaign_id: UUID, payload: CampaignUpdate
) -> CampaignRead:
    row = db.get(Campaign, campaign_id)
    if row is None:
        raise NotFound("Campaign not found.")
    if row.status in (CampaignStatus.completed, CampaignStatus.cancelled):
        raise RuleError("Cancelled or completed campaigns cannot be changed.", "BR-08")
    start = payload.start_date or row.start_date
    end = payload.end_date or row.end_date
    _check_dates_and_length(start, end, row.spot_length)
    if payload.planned_spots is not None:
        used = len(
            db.scalars(
                select(Booking).where(
                    Booking.campaign_id == row.id,
                    Booking.status.in_(COMMITTED),
                )
            ).all()
        )
        if payload.planned_spots < used:
            raise RuleError("Booked spots would exceed planned spots.", "BR-07")
        row.planned_spots = payload.planned_spots
    if payload.budget is not None:
        row.budget = payload.budget
    if payload.name is not None:
        row.name = payload.name.strip()
    if "agency_id" in payload.model_fields_set:
        if payload.agency_id is not None and db.get(Agency, payload.agency_id) is None:
            raise NotFound("Agency not found.")
        row.agency_id = payload.agency_id
    row.start_date = start
    row.end_date = end
    row.changed_by = user.id
    row.updated_at = utc_now()
    db.commit()
    return get_campaign(db, row.id)


def set_status(
    db: Session, user: User, campaign_id: UUID, payload: CampaignStatusUpdate
) -> CampaignRead:
    row = db.get(Campaign, campaign_id)
    if row is None:
        raise NotFound("Campaign not found.")
    if payload.status not in _TRANSITIONS[row.status]:
        raise RuleError(
            f"Cannot change a {row.status.value} campaign to {payload.status.value}.",
            "BR-08",
        )
    row.status = payload.status
    row.changed_by = user.id
    row.updated_at = utc_now()
    db.commit()
    return get_campaign(db, row.id)
