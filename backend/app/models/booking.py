import uuid
from decimal import Decimal

from sqlalchemy import ForeignKey, Index, Integer, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import ActorMixin, Base, TimestampMixin
from app.models.enums import BOOKING_STATUS, BookingStatus


class Booking(ActorMixin, TimestampMixin, Base):
    """Rows are never deleted. Cancel and as-run change status and append history."""

    __tablename__ = "bookings"
    __table_args__ = (
        Index("ix_bookings_ad_break_id", "ad_break_id"),
        Index("ix_bookings_campaign_id", "campaign_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=False
    )
    ad_break_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ad_breaks.id"), nullable=False
    )
    spot_length: Mapped[int] = mapped_column(Integer, nullable=False)
    cost: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    status: Mapped[BookingStatus] = mapped_column(
        BOOKING_STATUS, nullable=False, default=BookingStatus.booked
    )
