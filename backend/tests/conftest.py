# ruff: noqa: E402
import os

os.environ.pop("DATABASE_URL", None)
os.environ["DATABASE_NAME"] = "adbreak_test"
os.environ["JWT_SECRET"] = "test-secret"
os.environ["SEED_DEMO"] = "false"

import psycopg
import pytest
from sqlalchemy import text

from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models import (  # noqa: F401
    AdBreak,
    Advertiser,
    Agency,
    Booking,
    BookingStatusHistory,
    Campaign,
    Channel,
    RateCard,
    User,
)


def _ensure_database() -> None:
    conn = psycopg.connect(
        host=os.environ.get("DATABASE_HOST", "localhost"),
        port=os.environ.get("DATABASE_PORT", "5432"),
        user=os.environ.get("DATABASE_USER", "adbreak"),
        password=os.environ.get("DATABASE_PASSWORD", "adbreak"),
        dbname="postgres",
        autocommit=True,
    )
    exists = conn.execute(
        "SELECT 1 FROM pg_database WHERE datname = 'adbreak_test'"
    ).fetchone()
    if exists is None:
        conn.execute("CREATE DATABASE adbreak_test")
    conn.close()


_ensure_database()


@pytest.fixture(scope="session", autouse=True)
def _schema() -> None:
    Base.metadata.drop_all(engine)
    with engine.begin() as connection:
        connection.execute(text("DROP TYPE IF EXISTS booking_status CASCADE"))
        connection.execute(text("DROP TYPE IF EXISTS campaign_status CASCADE"))
        connection.execute(text("DROP TYPE IF EXISTS daypart CASCADE"))
        connection.execute(text("DROP TYPE IF EXISTS user_role CASCADE"))
    Base.metadata.create_all(engine)


@pytest.fixture(autouse=True)
def _clean() -> None:
    db = SessionLocal()
    db.execute(
        text(
            "TRUNCATE booking_status_history, bookings, ad_breaks, campaigns, "
            "advertisers, agencies, rate_card, channels, users CASCADE"
        )
    )
    db.commit()
    db.close()
