import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import ActorMixin, Base, TimestampMixin
from app.models.enums import CAMPAIGN_STATUS, CampaignStatus


class Campaign(ActorMixin, TimestampMixin, Base):
    __tablename__ = "campaigns"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    advertiser_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("advertisers.id"), nullable=False
    )
    agency_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("agencies.id"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    spot_length: Mapped[int] = mapped_column(Integer, nullable=False)
    planned_spots: Mapped[int] = mapped_column(Integer, nullable=False)
    budget: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    status: Mapped[CampaignStatus] = mapped_column(
        CAMPAIGN_STATUS, nullable=False, default=CampaignStatus.draft
    )
