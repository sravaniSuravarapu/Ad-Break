from collections import defaultdict
from datetime import date
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.ad_break import AdBreak
from app.models.advertiser import Advertiser
from app.models.booking import Booking
from app.models.campaign import Campaign
from app.models.channel import Channel
from app.models.enums import OCCUPYING, BookingStatus, Daypart
from app.schemas.dto import DeliveryRow, FillRow, RevenueReport, RevenueRow
from app.services.campaigns import list_campaigns


def fill_report(
    db: Session,
    channel_id: UUID | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    daypart: Daypart | None = None,
) -> list[FillRow]:
    stmt = select(AdBreak, Channel).join(Channel, Channel.id == AdBreak.channel_id)
    if channel_id is not None:
        stmt = stmt.where(AdBreak.channel_id == channel_id)
    if date_from is not None:
        stmt = stmt.where(AdBreak.break_date >= date_from)
    if date_to is not None:
        stmt = stmt.where(AdBreak.break_date <= date_to)
    if daypart is not None:
        stmt = stmt.where(AdBreak.daypart == daypart)
    used_rows = db.execute(
        select(Booking.ad_break_id, Booking.spot_length).where(Booking.status.in_(OCCUPYING))
    ).all()
    used: dict[UUID, int] = defaultdict(int)
    for break_id, seconds in used_rows:
        used[break_id] += int(seconds)
    grouped: dict[tuple[UUID, str, date, Daypart], list[int]] = defaultdict(lambda: [0, 0])
    for ad_break, channel in db.execute(stmt).all():
        key = (channel.id, channel.name, ad_break.break_date, ad_break.daypart)
        grouped[key][0] += ad_break.capacity_seconds
        grouped[key][1] += used.get(ad_break.id, 0)
    rows: list[FillRow] = []
    for (channel_key, channel_name, break_date, part), (capacity, booked) in sorted(
        grouped.items(), key=lambda item: (item[0][2], item[0][1], item[0][3].value)
    ):
        fill = round(booked / capacity * 100, 2) if capacity else 0.0
        rows.append(
            FillRow(
                channel_id=channel_key,
                channel_name=channel_name,
                break_date=break_date,
                daypart=part,
                capacity_seconds=capacity,
                booked_seconds=booked,
                fill_pct=fill,
            )
        )
    return rows


def delivery_report(db: Session) -> list[DeliveryRow]:
    return [
        DeliveryRow(
            campaign_id=row.id,
            campaign_name=row.name,
            advertiser_name=row.advertiser_name,
            planned_spots=row.planned_spots,
            spots_booked=row.spots_booked,
            spots_aired=row.spots_aired,
            spots_counting=row.spots_counting,
            delivery_pct=row.delivery_pct,
            budget=row.budget,
            booked_cost=row.booked_cost,
            budget_utilisation_pct=row.budget_utilisation_pct,
        )
        for row in list_campaigns(db)
    ]


def _sum_rows(pairs: list[tuple[str, Decimal]]) -> list[RevenueRow]:
    totals: dict[str, Decimal] = defaultdict(lambda: Decimal("0.00"))
    for name, amount in pairs:
        totals[name] += amount
    return [
        RevenueRow(name=name, revenue=amount)
        for name, amount in sorted(totals.items(), key=lambda item: item[1], reverse=True)
    ]


def revenue_report(db: Session) -> RevenueReport:
    # Revenue is aired spots x stored spot cost.
    rows = db.execute(
        select(Advertiser.name, Advertiser.category, Channel.name, Booking.cost)
        .join(Campaign, Campaign.id == Booking.campaign_id)
        .join(Advertiser, Advertiser.id == Campaign.advertiser_id)
        .join(AdBreak, AdBreak.id == Booking.ad_break_id)
        .join(Channel, Channel.id == AdBreak.channel_id)
        .where(Booking.status == BookingStatus.aired)
    ).all()
    return RevenueReport(
        by_advertiser=_sum_rows([(name, cost) for name, _category, _channel, cost in rows]),
        by_category=_sum_rows([(category, cost) for _name, category, _channel, cost in rows]),
        by_channel=_sum_rows([(channel, cost) for _name, _category, channel, cost in rows]),
    )
