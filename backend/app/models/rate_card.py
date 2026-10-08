import uuid
from decimal import Decimal

from sqlalchemy import Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import ActorMixin, Base, TimestampMixin
from app.models.enums import DAYPART, Daypart


class RateCard(ActorMixin, TimestampMixin, Base):
    __tablename__ = "rate_card"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    daypart: Mapped[Daypart] = mapped_column(DAYPART, unique=True, nullable=False)
    rate_per_10s: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
