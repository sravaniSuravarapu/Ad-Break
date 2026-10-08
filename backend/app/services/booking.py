from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.clock import utc_now, utc_today
from app.core.errors import NotFound, RuleError
from app.models.ad_break import AdBreak
from app.models.advertiser import Advertiser
from app.models.booking import Booking
from app.models.booking_status_history import BookingStatusHistory
from app.models.campaign import Campaign
from app.models.channel import Channel
from app.models.enums import ALLOWED_SPOT_LENGTHS, COMMITTED, OCCUPYING, BookingStatus, CampaignStatus
from app.models.rate_card import RateCard
from app.models.user import User
from app.schemas.dto import AsRunUpdate, BookingCreate, BookingMove, BookingRead, BookingRebook

_MONEY = Decimal("0.01")


def _cost(db: Session, spot_length: int, daypart: object) -> Decimal:
    # BR-06: cost comes from the rate card, never a hardcoded price.
    rate = db.scalar(select(RateCard).where(RateCard.daypart == daypart))
    if rate is None:
        raise RuleError("No rate is configured for this daypart.", "BR-06")
    return (Decimal(spot_length) / Decimal(10) * rate.rate_per_10s).quantize(_MONEY)


def _lock_campaign(db: Session, campaign_id: UUID) -> Campaign:
    row = db.scalar(select(Campaign).where(Campaign.id == campaign_id).with_for_update())
    if row is None:
        raise NotFound("Campaign not found.")
    return row


def _lock_breaks(db: Session, break_ids: list[UUID]) -> dict[UUID, AdBreak]:
    # BR-10: lock break rows in a stable order inside this transaction.
    rows = db.scalars(
        select(AdBreak).where(AdBreak.id.in_(break_ids)).order_by(AdBreak.id).with_for_update()
    ).all()
    found = {row.id: row for row in rows}
    missing = [str(break_id) for break_id in break_ids if break_id not in found]
    if missing:
        raise NotFound("Break not found.")
    return found


def _used_seconds(db: Session, break_id: UUID, exclude_booking_id: UUID | None) -> int:
    stmt = select(func.coalesce(func.sum(Booking.spot_length), 0)).where(
        Booking.ad_break_id == break_id,
        Booking.status.in_(OCCUPYING),
    )
    if exclude_booking_id is not None:
        stmt = stmt.where(Booking.id != exclude_booking_id)
    return int(db.scalar(stmt) or 0)


def _validate(
    db: Session,
    campaign: Campaign,
    ad_break: AdBreak,
    spot_length: int,
    exclude_booking_id: UUID | None,
) -> Decimal:
    # BR-01
    if spot_length not in ALLOWED_SPOT_LENGTHS:
        raise RuleError("Spot length must be one of 10, 15, 20, 30, 60 seconds.", "BR-01")
    if spot_length != campaign.spot_length:
        raise RuleError("Spot length must match the campaign spot length.", "BR-01")
    # BR-08
    if campaign.status in (CampaignStatus.cancelled, CampaignStatus.completed):
        raise RuleError("Cancelled or completed campaigns cannot be booked.", "BR-08")
    if campaign.status != CampaignStatus.active:
        raise RuleError("Only an active campaign can be booked.", "BR-08")
    # BR-02
    if not (campaign.start_date <= ad_break.break_date <= campaign.end_date):
        raise RuleError("Break date is outside the campaign dates.", "BR-02")
    used = _used_seconds(db, ad_break.id, exclude_booking_id)
    remaining = ad_break.capacity_seconds - used
    # BR-03
    if spot_length > remaining:
        raise RuleError(
            "Booked seconds would exceed break capacity.",
            "BR-03",
            remaining_seconds=remaining,
        )
    advertiser = db.get(Advertiser, campaign.advertiser_id)
    if advertiser is None:
        raise NotFound("Advertiser not found.")
    same_advertiser = db.scalar(
        select(Booking.id)
        .join(Campaign, Campaign.id == Booking.campaign_id)
        .where(
            Booking.ad_break_id == ad_break.id,
            Booking.status.in_(OCCUPYING),
            Campaign.advertiser_id == advertiser.id,
            *([Booking.id != exclude_booking_id] if exclude_booking_id is not None else []),
        )
    )
    if same_advertiser is not None:
        raise RuleError("Advertiser already has a spot in this break.", "BR-04")
    clash = db.scalar(
        select(Booking.id)
        .join(Campaign, Campaign.id == Booking.campaign_id)
        .join(Advertiser, Advertiser.id == Campaign.advertiser_id)
        .where(
            Booking.ad_break_id == ad_break.id,
            Booking.status.in_(OCCUPYING),
            Advertiser.category == advertiser.category,
            Advertiser.id != advertiser.id,
            *([Booking.id != exclude_booking_id] if exclude_booking_id is not None else []),
        )
    )
    if clash is not None:
        raise RuleError("Competitor category already booked in this break.", "BR-05")
    count_stmt = select(func.count(Booking.id)).where(
        Booking.campaign_id == campaign.id,
        Booking.status.in_(COMMITTED),
    )
    spent_stmt = select(func.coalesce(func.sum(Booking.cost), 0)).where(
        Booking.campaign_id == campaign.id,
        Booking.status.in_(COMMITTED),
    )
    if exclude_booking_id is not None:
        count_stmt = count_stmt.where(Booking.id != exclude_booking_id)
        spent_stmt = spent_stmt.where(Booking.id != exclude_booking_id)
    # BR-07
    if int(db.scalar(count_stmt) or 0) + 1 > campaign.planned_spots:
        raise RuleError("Booked spots would exceed planned spots.", "BR-07")
    cost = _cost(db, spot_length, ad_break.daypart)
    spent = Decimal(db.scalar(spent_stmt) or 0)
    # BR-06
    if spent + cost > campaign.budget:
        raise RuleError("Booking cost would exceed campaign budget.", "BR-06")
    return cost


def _history(
    db: Session,
    booking: Booking,
    old_status: BookingStatus | None,
    new_status: BookingStatus,
    user: User,
) -> None:
    now = utc_now()
    db.add(
        BookingStatusHistory(
            booking_id=booking.id,
            old_status=old_status,
            new_status=new_status,
            changed_by=user.id,
            created_by=user.id,
            changed_at=now,
            created_at=now,
            updated_at=now,
        )
    )


def _remaining(db: Session, break_id: UUID) -> int:
    ad_break = db.get(AdBreak, break_id)
    if ad_break is None:
        return 0
    return ad_break.capacity_seconds - _used_seconds(db, break_id, None)


def to_read(db: Session, booking: Booking) -> BookingRead:
    campaign = db.get(Campaign, booking.campaign_id)
    advertiser = db.get(Advertiser, campaign.advertiser_id) if campaign else None
    ad_break = db.get(AdBreak, booking.ad_break_id)
    channel = db.get(Channel, ad_break.channel_id) if ad_break else None
    if campaign is None or advertiser is None or ad_break is None or channel is None:
        raise NotFound("Booking not found.")
    return BookingRead(
        id=booking.id,
        campaign_id=campaign.id,
        campaign_name=campaign.name,
        advertiser_name=advertiser.name,
        category=advertiser.category,
        ad_break_id=ad_break.id,
        channel_name=channel.name,
        break_date=ad_break.break_date,
        start_time=ad_break.start_time,
        daypart=ad_break.daypart,
        spot_length=booking.spot_length,
        cost=booking.cost,
        status=booking.status,
        created_at=booking.created_at,
        remaining_seconds=_remaining(db, ad_break.id),
    )


def list_bookings(
    db: Session,
    campaign_id: UUID | None = None,
    ad_break_id: UUID | None = None,
    status: BookingStatus | None = None,
) -> list[BookingRead]:
    stmt = select(Booking).order_by(Booking.created_at.desc())
    if campaign_id is not None:
        stmt = stmt.where(Booking.campaign_id == campaign_id)
    if ad_break_id is not None:
        stmt = stmt.where(Booking.ad_break_id == ad_break_id)
    if status is not None:
        stmt = stmt.where(Booking.status == status)
    return [to_read(db, row) for row in db.scalars(stmt).all()]


def create_booking(db: Session, user: User, payload: BookingCreate) -> BookingRead:
    campaign = _lock_campaign(db, payload.campaign_id)
    ad_break = _lock_breaks(db, [payload.ad_break_id])[payload.ad_break_id]
    cost = _validate(db, campaign, ad_break, campaign.spot_length, None)
    now = utc_now()
    booking = Booking(
        campaign_id=campaign.id,
        ad_break_id=ad_break.id,
        spot_length=campaign.spot_length,
        cost=cost,
        status=BookingStatus.booked,
        created_by=user.id,
        changed_by=user.id,
        created_at=now,
        updated_at=now,
    )
    db.add(booking)
    db.flush()
    _history(db, booking, None, BookingStatus.booked, user)
    db.commit()
    db.refresh(booking)
    return to_read(db, booking)


def cancel_booking(db: Session, user: User, booking_id: UUID) -> BookingRead:
    booking = db.scalar(select(Booking).where(Booking.id == booking_id).with_for_update())
    if booking is None:
        raise NotFound("Booking not found.")
    if booking.status != BookingStatus.booked:
        raise RuleError("Only a booked spot can be cancelled.", "BR-09")
    ad_break = _lock_breaks(db, [booking.ad_break_id])[booking.ad_break_id]
    # BR-09: cancellation is allowed only before the break date.
    if ad_break.break_date <= utc_today():
        raise RuleError("A booking can be cancelled only before the break date.", "BR-09")
    old = booking.status
    booking.status = BookingStatus.cancelled
    booking.changed_by = user.id
    booking.updated_at = utc_now()
    _history(db, booking, old, BookingStatus.cancelled, user)
    db.commit()
    db.refresh(booking)
    return to_read(db, booking)


def move_booking(db: Session, user: User, booking_id: UUID, payload: BookingMove) -> BookingRead:
    booking = db.scalar(select(Booking).where(Booking.id == booking_id).with_for_update())
    if booking is None:
        raise NotFound("Booking not found.")
    if booking.status != BookingStatus.booked:
        raise RuleError("Only a booked spot can be moved.", "BOOKING")
    if payload.ad_break_id == booking.ad_break_id:
        raise RuleError("Pick a different break to move this spot.", "BOOKING")
    campaign = _lock_campaign(db, booking.campaign_id)
    locked = _lock_breaks(db, sorted([booking.ad_break_id, payload.ad_break_id]))
    target = locked[payload.ad_break_id]
    cost = _validate(db, campaign, target, booking.spot_length, booking.id)
    booking.ad_break_id = target.id
    booking.cost = cost
    booking.changed_by = user.id
    booking.updated_at = utc_now()
    db.commit()
    db.refresh(booking)
    return to_read(db, booking)


def rebook_booking(db: Session, user: User, booking_id: UUID, payload: BookingRebook) -> BookingRead:
    existing = db.get(Booking, booking_id)
    if existing is None:
        raise NotFound("Booking not found.")
    if existing.status != BookingStatus.cancelled:
        raise RuleError("Only a cancelled booking can be rebooked.", "BOOKING")
    # New row. The cancelled booking and its history stay in place.
    return create_booking(
        db,
        user,
        BookingCreate(campaign_id=existing.campaign_id, ad_break_id=payload.ad_break_id),
    )


def mark_as_run(db: Session, user: User, booking_id: UUID, payload: AsRunUpdate) -> BookingRead:
    if payload.status not in (BookingStatus.aired, BookingStatus.missed):
        raise RuleError("As-run status must be aired or missed.", "BR-09")
    booking = db.scalar(select(Booking).where(Booking.id == booking_id).with_for_update())
    if booking is None:
        raise NotFound("Booking not found.")
    if booking.status != BookingStatus.booked:
        raise RuleError("Only a booked spot can be marked aired or missed.", "BR-09")
    ad_break = _lock_breaks(db, [booking.ad_break_id])[booking.ad_break_id]
    if ad_break.break_date > utc_today():
        raise RuleError("As-run can be marked only on or after the break date.", "BR-09")
    old = booking.status
    booking.status = payload.status
    booking.changed_by = user.id
    booking.updated_at = utc_now()
    _history(db, booking, old, payload.status, user)
    db.commit()
    db.refresh(booking)
    return to_read(db, booking)
