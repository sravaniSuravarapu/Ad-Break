from datetime import time, timedelta
from decimal import Decimal

from sqlalchemy import select

from app.core.clock import utc_now, utc_today
from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.channel import Channel
from app.models.enums import BookingStatus, CampaignStatus, Daypart, UserRole
from app.models.rate_card import RateCard
from app.models.user import User
from app.schemas.dto import (
    AdvertiserCreate,
    AgencyCreate,
    AsRunUpdate,
    BookingCreate,
    BreakCreate,
    CampaignCreate,
    CampaignStatusUpdate,
    ChannelCreate,
    RateCardUpdate,
)
from app.services import booking as booking_service
from app.services import breaks as break_service
from app.services import campaigns as campaign_service
from app.services import catalog

# Demo prices only. Booking logic reads rate_card and does not use these numbers.
DEMO_RATES: dict[Daypart, Decimal] = {
    Daypart.morning: Decimal("8000.00"),
    Daypart.daytime: Decimal("6000.00"),
    Daypart.prime: Decimal("15000.00"),
    Daypart.late_night: Decimal("5000.00"),
}
DEMO_PASSWORD = "Demo@12345"
DEMO_USERS = (
    ("sales@example.com", UserRole.ad_sales_executive),
    ("traffic@example.com", UserRole.traffic_manager),
    ("revenue@example.com", UserRole.ad_revenue_head),
)
START_TIMES = {
    Daypart.morning: time(9, 0),
    Daypart.daytime: time(14, 0),
    Daypart.prime: time(20, 0),
    Daypart.late_night: time(23, 30),
}


def _user(db, email: str, role: UserRole) -> User:
    existing = db.scalar(select(User).where(User.email == email))
    if existing is not None:
        return existing
    now = utc_now()
    row = User(
        email=email,
        password_hash=hash_password(DEMO_PASSWORD),
        role=role,
        is_active=True,
        created_at=now,
        updated_at=now,
        created_by=None,
        changed_by=None,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def run() -> None:
    db = SessionLocal()
    try:
        users = {role: _user(db, email, role) for email, role in DEMO_USERS}
        revenue = users[UserRole.ad_revenue_head]
        traffic = users[UserRole.traffic_manager]
        sales = users[UserRole.ad_sales_executive]
        for daypart, rate in DEMO_RATES.items():
            if db.scalar(select(RateCard).where(RateCard.daypart == daypart)) is None:
                catalog.upsert_rate(db, revenue, daypart, RateCardUpdate(rate_per_10s=rate))
        if db.scalar(select(Channel).where(Channel.name == "Aurora TV")) is not None:
            return
        channels = [
            catalog.create_channel(db, traffic, ChannelCreate(name=name))
            for name in ("Aurora TV", "Metro News", "Coast Sports")
        ]
        today = utc_today()
        created_breaks: dict[tuple[str, int, Daypart], object] = {}
        for channel in channels:
            for offset in range(-1, 7):
                for daypart, start in START_TIMES.items():
                    created = break_service.create_break(
                        db,
                        traffic,
                        BreakCreate(
                            channel_id=channel.id,
                            break_date=today + timedelta(days=offset),
                            start_time=start,
                            daypart=daypart,
                            capacity_seconds=120,
                        ),
                    )
                    created_breaks[(channel.name, offset, daypart)] = created
        agency = catalog.create_agency(db, sales, AgencyCreate(name="Horizon Media"))
        northwind = catalog.create_advertiser(
            db,
            sales,
            AdvertiserCreate(name="Northwind Motors", category="Automotive", agency_id=agency.id),
        )
        catalog.create_advertiser(
            db,
            sales,
            AdvertiserCreate(name="Summit Motors", category="Automotive", agency_id=agency.id),
        )
        catalog.create_advertiser(
            db,
            sales,
            AdvertiserCreate(name="Bright Cola", category="Beverages", agency_id=agency.id),
        )
        campaign = campaign_service.create_campaign(
            db,
            sales,
            CampaignCreate(
                advertiser_id=northwind.id,
                agency_id=agency.id,
                name="Festive Drive",
                start_date=today - timedelta(days=1),
                end_date=today + timedelta(days=21),
                spot_length=30,
                planned_spots=10,
                budget=Decimal("500000.00"),
            ),
        )
        campaign_service.set_status(
            db, sales, campaign.id, CampaignStatusUpdate(status=CampaignStatus.active)
        )
        aired_break = created_breaks[("Aurora TV", -1, Daypart.prime)]
        booked = booking_service.create_booking(
            db,
            sales,
            BookingCreate(campaign_id=campaign.id, ad_break_id=aired_break.id),
        )
        booking_service.mark_as_run(
            db, traffic, booked.id, AsRunUpdate(status=BookingStatus.aired)
        )
        open_break = created_breaks[("Aurora TV", 0, Daypart.morning)]
        booking_service.create_booking(
            db,
            sales,
            BookingCreate(campaign_id=campaign.id, ad_break_id=open_break.id),
        )
    finally:
        db.close()


if __name__ == "__main__":
    run()
