from datetime import date
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.clock import utc_now
from app.core.errors import Conflict, NotFound, RuleError
from app.models.ad_break import AdBreak
from app.models.booking import Booking
from app.models.campaign import Campaign
from app.models.channel import Channel
from app.models.enums import COMMITTED, OCCUPYING, Daypart
from app.models.user import User
from app.schemas.dto import BreakCreate, BreakRead, BreakUpdate


def _used_seconds(db: Session) -> dict[UUID, int]:
    rows = db.execute(
        select(Booking.ad_break_id, func.coalesce(func.sum(Booking.spot_length), 0)).where(
            Booking.status.in_(OCCUPYING)
        ).group_by(Booking.ad_break_id)
    ).all()
    return {break_id: int(seconds) for break_id, seconds in rows}


def _to_read(row: AdBreak, channel_name: str, booked_seconds: int) -> BreakRead:
    remaining = row.capacity_seconds - booked_seconds
    fill = round(booked_seconds / row.capacity_seconds * 100, 2) if row.capacity_seconds else 0.0
    return BreakRead(
        id=row.id,
        channel_id=row.channel_id,
        channel_name=channel_name,
        break_date=row.break_date,
        start_time=row.start_time,
        daypart=row.daypart,
        capacity_seconds=row.capacity_seconds,
        booked_seconds=booked_seconds,
        remaining_seconds=remaining,
        fill_pct=fill,
    )


def list_breaks(
    db: Session,
    channel_id: UUID | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    daypart: Daypart | None = None,
) -> list[BreakRead]:
    stmt = (
        select(AdBreak, Channel.name)
        .join(Channel, Channel.id == AdBreak.channel_id)
        .order_by(AdBreak.break_date, AdBreak.start_time, Channel.name)
    )
    if channel_id is not None:
        stmt = stmt.where(AdBreak.channel_id == channel_id)
    if date_from is not None:
        stmt = stmt.where(AdBreak.break_date >= date_from)
    if date_to is not None:
        stmt = stmt.where(AdBreak.break_date <= date_to)
    if daypart is not None:
        stmt = stmt.where(AdBreak.daypart == daypart)
    used = _used_seconds(db)
    return [_to_read(row, name, used.get(row.id, 0)) for row, name in db.execute(stmt).all()]


def create_break(db: Session, user: User, payload: BreakCreate) -> BreakRead:
    if db.get(Channel, payload.channel_id) is None:
        raise NotFound("Channel not found.")
    if payload.capacity_seconds < 1:
        raise RuleError("Break capacity must be at least 1 second.", "BR-03")
    now = utc_now()
    row = AdBreak(
        channel_id=payload.channel_id,
        break_date=payload.break_date,
        start_time=payload.start_time,
        daypart=payload.daypart,
        capacity_seconds=payload.capacity_seconds,
        created_by=user.id,
        changed_by=user.id,
        created_at=now,
        updated_at=now,
    )
    db.add(row)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise Conflict("A break already exists for this channel, date, and start time.") from exc
    db.refresh(row)
    channel = db.get(Channel, row.channel_id)
    return _to_read(row, channel.name if channel else "", 0)


def update_break(db: Session, user: User, break_id: UUID, payload: BreakUpdate) -> BreakRead:
    row = db.scalar(select(AdBreak).where(AdBreak.id == break_id).with_for_update())
    if row is None:
        raise NotFound("Break not found.")
    booked = _used_seconds(db).get(row.id, 0)
    capacity = payload.capacity_seconds if payload.capacity_seconds is not None else row.capacity_seconds
    # BR-03: shrinking a break cannot drop below seconds already booked.
    if capacity < booked:
        raise RuleError(
            "Booked seconds would exceed break capacity.",
            "BR-03",
            remaining_seconds=row.capacity_seconds - booked,
        )
    new_date = payload.break_date or row.break_date
    if payload.break_date is not None:
        campaigns = db.scalars(
            select(Campaign)
            .join(Booking, Booking.campaign_id == Campaign.id)
            .where(Booking.ad_break_id == row.id, Booking.status.in_(COMMITTED))
        ).all()
        for campaign in campaigns:
            # BR-02
            if not (campaign.start_date <= new_date <= campaign.end_date):
                raise RuleError("Break date is outside the campaign dates.", "BR-02")
    row.capacity_seconds = capacity
    row.break_date = new_date
    if payload.start_time is not None:
        row.start_time = payload.start_time
    if payload.daypart is not None:
        row.daypart = payload.daypart
    row.changed_by = user.id
    row.updated_at = utc_now()
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise Conflict("A break already exists for this channel, date, and start time.") from exc
    db.refresh(row)
    channel = db.get(Channel, row.channel_id)
    return _to_read(row, channel.name if channel else "", booked)
