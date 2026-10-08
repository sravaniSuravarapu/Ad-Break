from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.clock import utc_now
from app.core.errors import Conflict, NotFound
from app.models.advertiser import Advertiser
from app.models.agency import Agency
from app.models.channel import Channel
from app.models.enums import Daypart
from app.models.rate_card import RateCard
from app.models.user import User
from app.schemas.dto import (
    AdvertiserCreate,
    AdvertiserRead,
    AdvertiserUpdate,
    AgencyCreate,
    AgencyRead,
    AgencyUpdate,
    ChannelCreate,
    ChannelRead,
    RateCardRead,
    RateCardUpdate,
)


def _touch(row: object, user: User) -> None:
    row.changed_by = user.id  # type: ignore[attr-defined]
    row.updated_at = utc_now()  # type: ignore[attr-defined]


def _commit(db: Session) -> None:
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise Conflict("A record with this name already exists.") from exc


def list_agencies(db: Session) -> list[AgencyRead]:
    rows = db.scalars(select(Agency).order_by(Agency.name)).all()
    return [AgencyRead.model_validate(row) for row in rows]


def create_agency(db: Session, user: User, payload: AgencyCreate) -> AgencyRead:
    now = utc_now()
    row = Agency(
        name=payload.name,
        created_by=user.id,
        changed_by=user.id,
        created_at=now,
        updated_at=now,
    )
    db.add(row)
    _commit(db)
    db.refresh(row)
    return AgencyRead.model_validate(row)


def update_agency(db: Session, user: User, agency_id: UUID, payload: AgencyUpdate) -> AgencyRead:
    row = db.get(Agency, agency_id)
    if row is None:
        raise NotFound("Agency not found.")
    row.name = payload.name
    _touch(row, user)
    _commit(db)
    db.refresh(row)
    return AgencyRead.model_validate(row)


def list_advertisers(db: Session) -> list[AdvertiserRead]:
    rows = db.scalars(select(Advertiser).order_by(Advertiser.name)).all()
    return [AdvertiserRead.model_validate(row) for row in rows]


def create_advertiser(db: Session, user: User, payload: AdvertiserCreate) -> AdvertiserRead:
    if payload.agency_id is not None and db.get(Agency, payload.agency_id) is None:
        raise NotFound("Agency not found.")
    now = utc_now()
    row = Advertiser(
        name=payload.name,
        category=payload.category,
        agency_id=payload.agency_id,
        created_by=user.id,
        changed_by=user.id,
        created_at=now,
        updated_at=now,
    )
    db.add(row)
    _commit(db)
    db.refresh(row)
    return AdvertiserRead.model_validate(row)


def update_advertiser(
    db: Session, user: User, advertiser_id: UUID, payload: AdvertiserUpdate
) -> AdvertiserRead:
    row = db.get(Advertiser, advertiser_id)
    if row is None:
        raise NotFound("Advertiser not found.")
    if payload.agency_id is not None and db.get(Agency, payload.agency_id) is None:
        raise NotFound("Agency not found.")
    if payload.name is not None:
        row.name = payload.name
    if payload.category is not None:
        row.category = payload.category
    if "agency_id" in payload.model_fields_set:
        row.agency_id = payload.agency_id
    _touch(row, user)
    _commit(db)
    db.refresh(row)
    return AdvertiserRead.model_validate(row)


def list_channels(db: Session) -> list[ChannelRead]:
    rows = db.scalars(select(Channel).order_by(Channel.name)).all()
    return [ChannelRead.model_validate(row) for row in rows]


def create_channel(db: Session, user: User, payload: ChannelCreate) -> ChannelRead:
    now = utc_now()
    row = Channel(
        name=payload.name,
        created_by=user.id,
        changed_by=user.id,
        created_at=now,
        updated_at=now,
    )
    db.add(row)
    _commit(db)
    db.refresh(row)
    return ChannelRead.model_validate(row)


def list_rate_card(db: Session) -> list[RateCardRead]:
    rows = db.scalars(select(RateCard).order_by(RateCard.daypart)).all()
    return [RateCardRead.model_validate(row) for row in rows]


def upsert_rate(db: Session, user: User, daypart: Daypart, payload: RateCardUpdate) -> RateCardRead:
    row = db.scalar(select(RateCard).where(RateCard.daypart == daypart))
    now = utc_now()
    if row is None:
        row = RateCard(
            daypart=daypart,
            rate_per_10s=payload.rate_per_10s,
            created_by=user.id,
            changed_by=user.id,
            created_at=now,
            updated_at=now,
        )
        db.add(row)
    else:
        row.rate_per_10s = payload.rate_per_10s
        _touch(row, user)
    _commit(db)
    db.refresh(row)
    return RateCardRead.model_validate(row)
