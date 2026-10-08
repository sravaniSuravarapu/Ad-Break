from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import require_roles
from app.db.session import get_db
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.dto import CampaignCreate, CampaignRead, CampaignStatusUpdate, CampaignUpdate
from app.services import campaigns as campaign_service

router = APIRouter(prefix="/campaigns", tags=["campaigns"])
_sales = require_roles(UserRole.ad_sales_executive)
_any = require_roles(UserRole.ad_sales_executive, UserRole.traffic_manager, UserRole.ad_revenue_head)


@router.get("", response_model=list[CampaignRead])
def list_campaigns(db: Session = Depends(get_db), _: User = Depends(_any)) -> list[CampaignRead]:
    return campaign_service.list_campaigns(db)


@router.post("", response_model=CampaignRead, status_code=201)
def create_campaign(
    payload: CampaignCreate,
    db: Session = Depends(get_db),
    user: User = Depends(_sales),
) -> CampaignRead:
    return campaign_service.create_campaign(db, user, payload)


@router.get("/{campaign_id}", response_model=CampaignRead)
def get_campaign(
    campaign_id: UUID,
    db: Session = Depends(get_db),
    _: User = Depends(_any),
) -> CampaignRead:
    return campaign_service.get_campaign(db, campaign_id)


@router.patch("/{campaign_id}", response_model=CampaignRead)
def update_campaign(
    campaign_id: UUID,
    payload: CampaignUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(_sales),
) -> CampaignRead:
    return campaign_service.update_campaign(db, user, campaign_id, payload)


@router.post("/{campaign_id}/status", response_model=CampaignRead)
def set_status(
    campaign_id: UUID,
    payload: CampaignStatusUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(_sales),
) -> CampaignRead:
    return campaign_service.set_status(db, user, campaign_id, payload)
