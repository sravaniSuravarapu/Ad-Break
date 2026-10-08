from datetime import timedelta
from uuid import UUID

import bcrypt
import jwt

from app.core.clock import utc_now
from app.core.config import settings

_ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    # passlib 1.7.4 cannot load bcrypt 5, so the hash uses the bcrypt library directly.
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), password_hash.encode())


def create_access_token(user_id: UUID, role: str) -> str:
    expire = utc_now() + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {"sub": str(user_id), "role": role, "exp": expire}
    return jwt.encode(payload, settings.jwt_secret, algorithm=_ALGORITHM)


def decode_access_token(token: str) -> dict[str, str]:
    data = jwt.decode(token, settings.jwt_secret, algorithms=[_ALGORITHM])
    return {"sub": str(data["sub"]), "role": str(data["role"])}
