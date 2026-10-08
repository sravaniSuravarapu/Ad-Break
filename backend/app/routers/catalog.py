from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import require_roles
from app.db.session import get_db
from app.models.enums import Daypart, UserRole
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
from app.services import catalog

router = APIRouter(tags=["catalog"])
_sales = require_roles(UserRole.ad_sales_executive)
_traffic = require_roles(UserRole.traffic_manager)
_revenue = require_roles(UserRole.ad_revenue_head)
_any = require_roles(UserRole.ad_sales_executive, UserRole.traffic_manager, UserRole.ad_revenue_head)


@router.get("/agencies", response_model=list[AgencyRead])
def list_agencies(db: Session = Depends(get_db), _: User = Depends(_any)) -> list[AgencyRead]:
    return catalog.list_agencies(db)


@router.post("/agencies", response_model=AgencyRead, status_code=201)
def create_agency(
    payload: AgencyCreate,
    db: Session = Depends(get_db),
    user: User = Depends(_sales),
) -> AgencyRead:
    return catalog.create_agency(db, user, payload)


@router.patch("/agencies/{agency_id}", response_model=AgencyRead)
def update_agency(
    agency_id: UUID,
    payload: AgencyUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(_sales),
) -> AgencyRead:
    return catalog.update_agency(db, user, agency_id, payload)


@router.get("/advertisers", response_model=list[AdvertiserRead])
def list_advertisers(
    db: Session = Depends(get_db), _: User = Depends(_any)
) -> list[AdvertiserRead]:
    return catalog.list_advertisers(db)


@router.post("/advertisers", response_model=AdvertiserRead, status_code=201)
def create_advertiser(
    payload: AdvertiserCreate,
    db: Session = Depends(get_db),
    user: User = Depends(_sales),
) -> AdvertiserRead:
    return catalog.create_advertiser(db, user, payload)


@router.patch("/advertisers/{advertiser_id}", response_model=AdvertiserRead)
def update_advertiser(
    advertiser_id: UUID,
    payload: AdvertiserUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(_sales),
) -> AdvertiserRead:
    return catalog.update_advertiser(db, user, advertiser_id, payload)


@router.get("/channels", response_model=list[ChannelRead])
def list_channels(db: Session = Depends(get_db), _: User = Depends(_any)) -> list[ChannelRead]:
    return catalog.list_channels(db)


@router.post("/channels", response_model=ChannelRead, status_code=201)
def create_channel(
    payload: ChannelCreate,
    db: Session = Depends(get_db),
    user: User = Depends(_traffic),
) -> ChannelRead:
    return catalog.create_channel(db, user, payload)


@router.get("/rate-card", response_model=list[RateCardRead])
def list_rate_card(db: Session = Depends(get_db), _: User = Depends(_any)) -> list[RateCardRead]:
    return catalog.list_rate_card(db)


@router.put("/rate-card/{daypart}", response_model=RateCardRead)
def upsert_rate(
    daypart: Daypart,
    payload: RateCardUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(_revenue),
) -> RateCardRead:
    return catalog.upsert_rate(db, user, daypart, payload)
