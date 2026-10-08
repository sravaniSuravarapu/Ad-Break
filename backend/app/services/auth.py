from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.clock import utc_now
from app.core.errors import AppError, Conflict, NotFound
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.schemas.dto import LoginRequest, SignupRequest, TokenResponse, TokenUser


def _token(user: User) -> TokenResponse:
    return TokenResponse(
        access_token=create_access_token(user.id, user.role.value),
        user=TokenUser.model_validate(user),
    )


def signup(db: Session, payload: SignupRequest) -> TokenResponse:
    now = utc_now()
    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        role=payload.role,
        is_active=True,
        created_at=now,
        updated_at=now,
        created_by=None,
        changed_by=None,
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise Conflict("An account with this email already exists.") from exc
    db.refresh(user)
    return _token(user)


def login(db: Session, payload: LoginRequest) -> TokenResponse:
    user = db.scalar(select(User).where(User.email == payload.email))
    if user is None or not user.is_active or not verify_password(payload.password, user.password_hash):
        raise AppError("Email or password is incorrect.", 401)
    return _token(user)


def get_user(db: Session, user_id: UUID) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise NotFound("User not found.")
    return user
