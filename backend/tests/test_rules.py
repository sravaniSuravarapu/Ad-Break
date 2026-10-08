from datetime import timedelta
from decimal import Decimal
from threading import Barrier, Thread
from uuid import UUID, uuid4

import httpx
import pytest

from app.core.clock import utc_today
from app.core.errors import RuleError
from app.db.session import SessionLocal
from app.main import app
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.dto import BookingCreate
from app.services import booking as booking_service

PASSWORD = "Demo@12345"


@pytest.fixture
def client():
    transport = httpx.ASGITransport(app=app)
    with httpx.Client(transport=transport, base_url="http://test") as http:
        yield http


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _signup(client: httpx.Client, role: str) -> str:
    email = f"{role}-{uuid4().hex[:8]}@example.com"
    response = client.post(
        "/api/v1/auth/signup",
        json={"email": email, "password": PASSWORD, "role": role},
    )
    assert response.status_code == 201, response.text
    return response.json()["access_token"]


def _rates(client: httpx.Client, revenue: str, rate: str = "10000.00") -> None:
    for daypart in ("morning", "daytime", "prime", "late_night"):
        response = client.put(
            f"/api/v1/rate-card/{daypart}",
            headers=_auth(revenue),
            json={"rate_per_10s": rate},
        )
        assert response.status_code == 200, response.text


def _channel(client: httpx.Client, traffic: str, name: str | None = None) -> str:
    response = client.post(
        "/api/v1/channels",
        headers=_auth(traffic),
        json={"name": name or f"Channel {uuid4().hex[:6]}"},
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def _break(
    client: httpx.Client,
    traffic: str,
    channel_id: str,
    day_offset: int,
    daypart: str = "prime",
    start: str = "20:00:00",
    capacity: int = 120,
) -> dict:
    response = client.post(
        "/api/v1/breaks",
        headers=_auth(traffic),
        json={
            "channel_id": channel_id,
            "break_date": str(utc_today() + timedelta(days=day_offset)),
            "start_time": start,
            "daypart": daypart,
            "capacity_seconds": capacity,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def _advertiser(client: httpx.Client, sales: str, name: str, category: str) -> str:
    response = client.post(
        "/api/v1/advertisers",
        headers=_auth(sales),
        json={"name": name, "category": category},
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def _campaign(
    client: httpx.Client,
    sales: str,
    advertiser_id: str,
    spot_length: int = 30,
    planned: int = 10,
    budget: str = "500000.00",
    start_offset: int = 0,
    end_offset: int = 14,
    activate: bool = True,
) -> dict:
    response = client.post(
        "/api/v1/campaigns",
        headers=_auth(sales),
        json={
            "advertiser_id": advertiser_id,
            "name": f"Campaign {uuid4().hex[:6]}",
            "start_date": str(utc_today() + timedelta(days=start_offset)),
            "end_date": str(utc_today() + timedelta(days=end_offset)),
            "spot_length": spot_length,
            "planned_spots": planned,
            "budget": budget,
        },
    )
    assert response.status_code == 201, response.text
    created = response.json()
    if activate:
        status = client.post(
            f"/api/v1/campaigns/{created['id']}/status",
            headers=_auth(sales),
            json={"status": "active"},
        )
        assert status.status_code == 200, status.text
        return status.json()
    return created


def _book(client: httpx.Client, sales: str, campaign_id: str, break_id: str) -> httpx.Response:
    return client.post(
        "/api/v1/bookings",
        headers=_auth(sales),
        json={"campaign_id": campaign_id, "ad_break_id": break_id},
    )


def test_br01_campaign_dates_and_spot_length(client: httpx.Client) -> None:
    sales = _signup(client, "ad_sales_executive")
    advertiser_id = _advertiser(client, sales, f"Adv {uuid4().hex[:6]}", "Retail")
    today = str(utc_today())
    bad_dates = client.post(
        "/api/v1/campaigns",
        headers=_auth(sales),
        json={
            "advertiser_id": advertiser_id,
            "name": "Bad dates",
            "start_date": today,
            "end_date": str(utc_today() - timedelta(days=1)),
            "spot_length": 30,
            "planned_spots": 1,
            "budget": "1000.00",
        },
    )
    assert bad_dates.status_code == 422
    assert bad_dates.json()["detail"]["rule"] == "BR-01"
    bad_length = client.post(
        "/api/v1/campaigns",
        headers=_auth(sales),
        json={
            "advertiser_id": advertiser_id,
            "name": "Bad length",
            "start_date": today,
            "end_date": today,
            "spot_length": 25,
            "planned_spots": 1,
            "budget": "1000.00",
        },
    )
    assert bad_length.status_code == 422
    assert bad_length.json()["detail"]["rule"] == "BR-01"


def test_br02_rejects_break_outside_campaign_dates(client: httpx.Client) -> None:
    sales = _signup(client, "ad_sales_executive")
    traffic = _signup(client, "traffic_manager")
    revenue = _signup(client, "ad_revenue_head")
    _rates(client, revenue)
    channel_id = _channel(client, traffic)
    later = _break(client, traffic, channel_id, 10, start="20:00:00")
    advertiser_id = _advertiser(client, sales, f"Adv {uuid4().hex[:6]}", "Retail")
    campaign = _campaign(client, sales, advertiser_id, end_offset=2)
    response = _book(client, sales, campaign["id"], later["id"])
    assert response.status_code == 422
    assert response.json()["detail"]["rule"] == "BR-02"


def test_br03_rejects_over_capacity_and_returns_remaining_seconds(client: httpx.Client) -> None:
    sales = _signup(client, "ad_sales_executive")
    traffic = _signup(client, "traffic_manager")
    revenue = _signup(client, "ad_revenue_head")
    _rates(client, revenue)
    channel_id = _channel(client, traffic)
    small = _break(client, traffic, channel_id, 1, start="20:00:00", capacity=50)
    other = _break(client, traffic, channel_id, 1, start="21:00:00", capacity=120)
    tight = _break(client, traffic, channel_id, 2, start="20:00:00", capacity=20)
    first_advertiser = _advertiser(client, sales, f"Adv A {uuid4().hex[:6]}", "Retail")
    second_advertiser = _advertiser(client, sales, f"Adv B {uuid4().hex[:6]}", "Finance")
    first_campaign = _campaign(client, sales, first_advertiser, spot_length=30)
    second_campaign = _campaign(client, sales, second_advertiser, spot_length=30)
    first = _book(client, sales, first_campaign["id"], small["id"])
    assert first.status_code == 201, first.text
    second = _book(client, sales, second_campaign["id"], small["id"])
    assert second.status_code == 422
    detail = second.json()["detail"]
    assert detail["rule"] == "BR-03"
    assert detail["remaining_seconds"] == 20
    parked = _book(client, sales, first_campaign["id"], other["id"])
    assert parked.status_code == 201, parked.text
    onto_tight = client.post(
        f"/api/v1/bookings/{parked.json()['id']}/move",
        headers=_auth(sales),
        json={"ad_break_id": tight["id"]},
    )
    assert onto_tight.status_code == 422
    assert onto_tight.json()["detail"]["rule"] == "BR-03"
    assert onto_tight.json()["detail"]["remaining_seconds"] == 20


def test_br04_rejects_second_spot_for_same_advertiser(client: httpx.Client) -> None:
    sales = _signup(client, "ad_sales_executive")
    traffic = _signup(client, "traffic_manager")
    revenue = _signup(client, "ad_revenue_head")
    _rates(client, revenue)
    channel_id = _channel(client, traffic)
    slot = _break(client, traffic, channel_id, 1)
    advertiser_id = _advertiser(client, sales, f"Adv {uuid4().hex[:6]}", "Retail")
    first_campaign = _campaign(client, sales, advertiser_id, spot_length=10, planned=2)
    second_campaign = _campaign(client, sales, advertiser_id, spot_length=10, planned=2)
    assert _book(client, sales, first_campaign["id"], slot["id"]).status_code == 201
    again = _book(client, sales, second_campaign["id"], slot["id"])
    assert again.status_code == 422
    assert again.json()["detail"]["rule"] == "BR-04"


def test_br05_rejects_exact_category_match(client: httpx.Client) -> None:
    sales = _signup(client, "ad_sales_executive")
    traffic = _signup(client, "traffic_manager")
    revenue = _signup(client, "ad_revenue_head")
    _rates(client, revenue)
    channel_id = _channel(client, traffic)
    slot = _break(client, traffic, channel_id, 1, capacity=120)
    auto_a = _advertiser(client, sales, f"Auto A {uuid4().hex[:4]}", "Automotive")
    auto_b = _advertiser(client, sales, f"Auto B {uuid4().hex[:4]}", "Automotive")
    cola = _advertiser(client, sales, f"Cola {uuid4().hex[:4]}", "Beverages")
    campaign_a = _campaign(client, sales, auto_a, spot_length=10)
    campaign_b = _campaign(client, sales, auto_b, spot_length=10)
    campaign_c = _campaign(client, sales, cola, spot_length=10)
    assert _book(client, sales, campaign_a["id"], slot["id"]).status_code == 201
    clash = _book(client, sales, campaign_b["id"], slot["id"])
    assert clash.status_code == 422
    assert clash.json()["detail"]["rule"] == "BR-05"
    other = _book(client, sales, campaign_c["id"], slot["id"])
    assert other.status_code == 201, other.text


def test_br06_computes_cost_from_rate_card_and_rejects_over_budget(client: httpx.Client) -> None:
    sales = _signup(client, "ad_sales_executive")
    traffic = _signup(client, "traffic_manager")
    revenue = _signup(client, "ad_revenue_head")
    _rates(client, revenue, "10000.00")
    channel_id = _channel(client, traffic)
    first_break = _break(client, traffic, channel_id, 1, start="20:00:00")
    second_break = _break(client, traffic, channel_id, 1, start="20:30:00")
    advertiser_id = _advertiser(client, sales, f"Adv {uuid4().hex[:6]}", "Retail")
    campaign = _campaign(client, sales, advertiser_id, spot_length=30, budget="50000.00")
    booked = _book(client, sales, campaign["id"], first_break["id"])
    assert booked.status_code == 201, booked.text
    assert Decimal(booked.json()["cost"]) == Decimal("30000.00")
    over = _book(client, sales, campaign["id"], second_break["id"])
    assert over.status_code == 422
    assert over.json()["detail"]["rule"] == "BR-06"


def test_br07_rejects_over_planned_spots(client: httpx.Client) -> None:
    sales = _signup(client, "ad_sales_executive")
    traffic = _signup(client, "traffic_manager")
    revenue = _signup(client, "ad_revenue_head")
    _rates(client, revenue)
    channel_id = _channel(client, traffic)
    first_break = _break(client, traffic, channel_id, 1, start="20:00:00")
    second_break = _break(client, traffic, channel_id, 2, start="20:00:00")
    advertiser_id = _advertiser(client, sales, f"Adv {uuid4().hex[:6]}", "Retail")
    campaign = _campaign(client, sales, advertiser_id, planned=1)
    assert _book(client, sales, campaign["id"], first_break["id"]).status_code == 201
    extra = _book(client, sales, campaign["id"], second_break["id"])
    assert extra.status_code == 422
    assert extra.json()["detail"]["rule"] == "BR-07"


def test_br08_rejects_draft_cancelled_and_completed(client: httpx.Client) -> None:
    sales = _signup(client, "ad_sales_executive")
    traffic = _signup(client, "traffic_manager")
    revenue = _signup(client, "ad_revenue_head")
    _rates(client, revenue)
    channel_id = _channel(client, traffic)
    slot = _break(client, traffic, channel_id, 1)
    advertiser_id = _advertiser(client, sales, f"Adv {uuid4().hex[:6]}", "Retail")
    draft = _campaign(client, sales, advertiser_id, activate=False)
    draft_book = _book(client, sales, draft["id"], slot["id"])
    assert draft_book.status_code == 422
    assert draft_book.json()["detail"]["rule"] == "BR-08"
    active = _campaign(client, sales, advertiser_id)
    cancelled = client.post(
        f"/api/v1/campaigns/{active['id']}/status",
        headers=_auth(sales),
        json={"status": "cancelled"},
    )
    assert cancelled.status_code == 200, cancelled.text
    cancelled_book = _book(client, sales, active["id"], slot["id"])
    assert cancelled_book.status_code == 422
    assert cancelled_book.json()["detail"]["rule"] == "BR-08"
    another = _campaign(client, sales, advertiser_id)
    completed = client.post(
        f"/api/v1/campaigns/{another['id']}/status",
        headers=_auth(sales),
        json={"status": "completed"},
    )
    assert completed.status_code == 200, completed.text
    completed_book = _book(client, sales, another["id"], slot["id"])
    assert completed_book.status_code == 422
    assert completed_book.json()["detail"]["rule"] == "BR-08"


def test_br09_traffic_manager_breaks_as_run_and_cancel_window(client: httpx.Client) -> None:
    sales = _signup(client, "ad_sales_executive")
    traffic = _signup(client, "traffic_manager")
    revenue = _signup(client, "ad_revenue_head")
    _rates(client, revenue)
    channel_id = _channel(client, traffic)
    denied = client.post(
        "/api/v1/breaks",
        headers=_auth(sales),
        json={
            "channel_id": channel_id,
            "break_date": str(utc_today() + timedelta(days=1)),
            "start_time": "18:00:00",
            "daypart": "prime",
            "capacity_seconds": 120,
        },
    )
    assert denied.status_code == 403
    today_break = _break(client, traffic, channel_id, 0, start="09:00:00", daypart="morning")
    future_break = _break(client, traffic, channel_id, 3, start="09:00:00", daypart="morning")
    advertiser_id = _advertiser(client, sales, f"Adv {uuid4().hex[:6]}", "Retail")
    campaign = _campaign(client, sales, advertiser_id, start_offset=-1, planned=4)
    today_booking = _book(client, sales, campaign["id"], today_break["id"])
    future_booking = _book(client, sales, campaign["id"], future_break["id"])
    assert today_booking.status_code == 201, today_booking.text
    assert future_booking.status_code == 201, future_booking.text
    too_late = client.post(
        f"/api/v1/bookings/{today_booking.json()['id']}/cancel",
        headers=_auth(sales),
    )
    assert too_late.status_code == 422
    assert too_late.json()["detail"]["rule"] == "BR-09"
    cancelled = client.post(
        f"/api/v1/bookings/{future_booking.json()['id']}/cancel",
        headers=_auth(sales),
    )
    assert cancelled.status_code == 200, cancelled.text
    assert cancelled.json()["status"] == "cancelled"
    rebooked = client.post(
        f"/api/v1/bookings/{future_booking.json()['id']}/rebook",
        headers=_auth(sales),
        json={"ad_break_id": future_break["id"]},
    )
    assert rebooked.status_code == 201, rebooked.text
    sales_mark = client.post(
        f"/api/v1/bookings/{today_booking.json()['id']}/as-run",
        headers=_auth(sales),
        json={"status": "aired"},
    )
    assert sales_mark.status_code == 403
    marked = client.post(
        f"/api/v1/bookings/{today_booking.json()['id']}/as-run",
        headers=_auth(traffic),
        json={"status": "aired"},
    )
    assert marked.status_code == 200, marked.text
    assert marked.json()["status"] == "aired"


def test_br10_concurrent_bookings_cannot_overbook(client: httpx.Client) -> None:
    sales_token = _signup(client, "ad_sales_executive")
    traffic = _signup(client, "traffic_manager")
    revenue = _signup(client, "ad_revenue_head")
    _rates(client, revenue)
    channel_id = _channel(client, traffic)
    slot = _break(client, traffic, channel_id, 1, start="22:00:00", capacity=30)
    advertiser_id = _advertiser(client, sales_token, f"Adv {uuid4().hex[:6]}", "Retail")
    campaign = _campaign(client, sales_token, advertiser_id, spot_length=20, planned=5)
    me = client.get("/api/v1/auth/me", headers=_auth(sales_token))
    assert me.status_code == 200, me.text
    user = User(
        id=UUID(me.json()["id"]),
        email=me.json()["email"],
        password_hash="x",
        role=UserRole.ad_sales_executive,
        is_active=True,
    )
    barrier = Barrier(2)
    results: list[str] = []

    def attempt() -> None:
        db = SessionLocal()
        try:
            barrier.wait()
            booking_service.create_booking(
                db,
                user,
                BookingCreate(campaign_id=campaign["id"], ad_break_id=slot["id"]),
            )
            results.append("ok")
        except RuleError as exc:
            results.append(exc.rule)
        finally:
            db.close()

    threads = [Thread(target=attempt), Thread(target=attempt)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    assert sorted(results) == ["BR-03", "ok"]
