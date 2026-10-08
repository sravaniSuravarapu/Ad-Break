from datetime import date, datetime, time
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.models.enums import ALLOWED_SPOT_LENGTHS, BookingStatus, CampaignStatus, Daypart, UserRole


class TokenUser(BaseModel):
    id: UUID
    email: str
    role: UserRole
    is_active: bool

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: TokenUser


class SignupRequest(BaseModel):
    email: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=8, max_length=72)
    role: UserRole

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        email = value.strip().lower()
        if "@" not in email or email.startswith("@") or email.endswith("@"):
            raise ValueError("Invalid email")
        return email


class LoginRequest(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()


class AgencyCreate(BaseModel):
    name: str = Field(min_length=1, max_length=160)

    @field_validator("name")
    @classmethod
    def strip_name(cls, value: str) -> str:
        return value.strip()


class AgencyUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=160)

    @field_validator("name")
    @classmethod
    def strip_name(cls, value: str) -> str:
        return value.strip()


class AgencyRead(BaseModel):
    id: UUID
    name: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AdvertiserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    category: str = Field(min_length=1, max_length=80)
    agency_id: UUID | None = None

    @field_validator("name", "category")
    @classmethod
    def strip_text(cls, value: str) -> str:
        return value.strip()


class AdvertiserUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=160)
    category: str | None = Field(default=None, min_length=1, max_length=80)
    agency_id: UUID | None = None

    @field_validator("name", "category")
    @classmethod
    def strip_text(cls, value: str | None) -> str | None:
        return value.strip() if value is not None else None


class AdvertiserRead(BaseModel):
    id: UUID
    name: str
    category: str
    agency_id: UUID | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CampaignCreate(BaseModel):
    advertiser_id: UUID
    agency_id: UUID | None = None
    name: str = Field(min_length=1, max_length=160)
    start_date: date
    end_date: date
    spot_length: int
    planned_spots: int = Field(ge=1)
    budget: Decimal = Field(ge=0, max_digits=12, decimal_places=2)

    @field_validator("name")
    @classmethod
    def strip_name(cls, value: str) -> str:
        return value.strip()


class CampaignUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=160)
    agency_id: UUID | None = None
    start_date: date | None = None
    end_date: date | None = None
    planned_spots: int | None = Field(default=None, ge=1)
    budget: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)


class CampaignStatusUpdate(BaseModel):
    status: CampaignStatus


class CampaignRead(BaseModel):
    id: UUID
    advertiser_id: UUID
    advertiser_name: str
    agency_id: UUID | None
    name: str
    start_date: date
    end_date: date
    spot_length: int
    planned_spots: int
    budget: Decimal
    status: CampaignStatus
    spots_booked: int
    spots_aired: int
    spots_missed: int
    spots_counting: int
    booked_cost: Decimal
    delivery_pct: float
    budget_utilisation_pct: float
    created_at: datetime


class ChannelCreate(BaseModel):
    name: str = Field(min_length=1, max_length=160)

    @field_validator("name")
    @classmethod
    def strip_name(cls, value: str) -> str:
        return value.strip()


class ChannelRead(BaseModel):
    id: UUID
    name: str
    created_at: datetime

    model_config = {"from_attributes": True}


class RateCardUpdate(BaseModel):
    rate_per_10s: Decimal = Field(gt=0, max_digits=12, decimal_places=2)


class RateCardRead(BaseModel):
    daypart: Daypart
    rate_per_10s: Decimal
    updated_at: datetime

    model_config = {"from_attributes": True}


class BreakCreate(BaseModel):
    channel_id: UUID
    break_date: date
    start_time: time
    daypart: Daypart
    capacity_seconds: int = 120


class BreakUpdate(BaseModel):
    break_date: date | None = None
    start_time: time | None = None
    daypart: Daypart | None = None
    capacity_seconds: int | None = Field(default=None, ge=1)


class BreakRead(BaseModel):
    id: UUID
    channel_id: UUID
    channel_name: str
    break_date: date
    start_time: time
    daypart: Daypart
    capacity_seconds: int
    booked_seconds: int
    remaining_seconds: int
    fill_pct: float


class BookingCreate(BaseModel):
    campaign_id: UUID
    ad_break_id: UUID


class BookingMove(BaseModel):
    ad_break_id: UUID


class BookingRebook(BaseModel):
    ad_break_id: UUID


class AsRunUpdate(BaseModel):
    status: BookingStatus


class BookingRead(BaseModel):
    id: UUID
    campaign_id: UUID
    campaign_name: str
    advertiser_name: str
    category: str
    ad_break_id: UUID
    channel_name: str
    break_date: date
    start_time: time
    daypart: Daypart
    spot_length: int
    cost: Decimal
    status: BookingStatus
    created_at: datetime
    remaining_seconds: int


class FillRow(BaseModel):
    channel_id: UUID
    channel_name: str
    break_date: date
    daypart: Daypart
    capacity_seconds: int
    booked_seconds: int
    fill_pct: float


class DeliveryRow(BaseModel):
    campaign_id: UUID
    campaign_name: str
    advertiser_name: str
    planned_spots: int
    spots_booked: int
    spots_aired: int
    spots_counting: int
    delivery_pct: float
    budget: Decimal
    booked_cost: Decimal
    budget_utilisation_pct: float


class RevenueRow(BaseModel):
    name: str
    revenue: Decimal


class RevenueReport(BaseModel):
    by_advertiser: list[RevenueRow]
    by_category: list[RevenueRow]
    by_channel: list[RevenueRow]


class HealthResponse(BaseModel):
    status: str


SPOT_LENGTHS = sorted(ALLOWED_SPOT_LENGTHS)
