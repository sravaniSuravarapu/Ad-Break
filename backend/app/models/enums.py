import enum

from sqlalchemy import Enum


class UserRole(enum.StrEnum):
    ad_sales_executive = "ad_sales_executive"
    traffic_manager = "traffic_manager"
    ad_revenue_head = "ad_revenue_head"


class Daypart(enum.StrEnum):
    morning = "morning"
    daytime = "daytime"
    prime = "prime"
    late_night = "late_night"


class CampaignStatus(enum.StrEnum):
    draft = "draft"
    active = "active"
    completed = "completed"
    cancelled = "cancelled"


class BookingStatus(enum.StrEnum):
    booked = "booked"
    aired = "aired"
    missed = "missed"
    cancelled = "cancelled"


def pg_enum(enum_cls: type[enum.StrEnum], name: str) -> Enum:
    return Enum(
        enum_cls,
        name=name,
        native_enum=True,
        values_callable=lambda members: [member.value for member in members],
    )


USER_ROLE = pg_enum(UserRole, "user_role")
DAYPART = pg_enum(Daypart, "daypart")
CAMPAIGN_STATUS = pg_enum(CampaignStatus, "campaign_status")
BOOKING_STATUS = pg_enum(BookingStatus, "booking_status")

ALLOWED_SPOT_LENGTHS = frozenset({10, 15, 20, 30, 60})
# Seconds that still hold break capacity. Missed and cancelled free the break.
OCCUPYING = (BookingStatus.booked, BookingStatus.aired)
# Spots that still count against planned spots and budget. Cancelled does not.
COMMITTED = (BookingStatus.booked, BookingStatus.aired, BookingStatus.missed)
