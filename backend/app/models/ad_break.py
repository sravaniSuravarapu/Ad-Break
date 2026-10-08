import uuid
from datetime import date, time

from sqlalchemy import Date, ForeignKey, Index, Integer, Time, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import ActorMixin, Base, TimestampMixin
from app.models.enums import DAYPART, Daypart


class AdBreak(ActorMixin, TimestampMixin, Base):
    __tablename__ = "ad_breaks"
    __table_args__ = (
        UniqueConstraint(
            "channel_id",
            "break_date",
            "start_time",
            name="uq_ad_breaks_channel_date_start",
        ),
        Index("ix_ad_breaks_channel_date_daypart", "channel_id", "break_date", "daypart"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    channel_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("channels.id"), nullable=False
    )
    break_date: Mapped[date] = mapped_column(Date, nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    daypart: Mapped[Daypart] = mapped_column(DAYPART, nullable=False)
    capacity_seconds: Mapped[int] = mapped_column(Integer, nullable=False, server_default="120")
