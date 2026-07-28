import os
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

_tmp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp_db.name}"
os.environ.setdefault("SESSION_SECRET_KEY", "test-secret")

from types import SimpleNamespace
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from webapp.db import (
    MONTHLY_SEARCH_LIMIT,
    EarlyAccessSignup,
    SessionLocal,
    User,
    hash_password,
    try_consume_search,
)
from webapp.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_landing_page_loads(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert "Sowld" in resp.text


def test_app_requires_login(client):
    resp = client.get("/app", follow_redirects=False)
    assert resp.status_code == 303
    assert resp.headers["location"] == "/login"


def test_signup_then_redirect_to_app(client):
    resp = client.post(
        "/signup",
        data={"email": "signup1@example.com", "password": "supersecret123"},
        follow_redirects=False,
    )
    assert resp.status_code == 303
    assert resp.headers["location"] == "/app"


def test_signup_duplicate_email_rejected(client):
    client.post("/signup", data={"email": "dup@example.com", "password": "supersecret123"})
    other_client = TestClient(app)
    resp = other_client.post("/signup", data={"email": "dup@example.com", "password": "anotherpass"})
    assert resp.status_code == 400
    assert "già registrata" in resp.text


def test_unsubscribed_user_sees_subscribe_page(client):
    client.post("/signup", data={"email": "nosub@example.com", "password": "supersecret123"})
    resp = client.get("/app")
    assert resp.status_code == 200
    assert "Abbonati" in resp.text


def test_login_wrong_password_rejected():
    signup_client = TestClient(app)
    signup_client.post(
        "/signup", data={"email": "wrongpw@example.com", "password": "correctpassword"}
    )
    fresh_client = TestClient(app)
    resp = fresh_client.post(
        "/login", data={"email": "wrongpw@example.com", "password": "nope"}
    )
    assert resp.status_code == 400


def test_billing_checkout_without_stripe_config_returns_503(client):
    client.post("/signup", data={"email": "checkout@example.com", "password": "supersecret123"})
    resp = client.get("/billing/checkout", follow_redirects=False)
    assert resp.status_code == 503


def _fake_paid_session(email):
    return SimpleNamespace(
        payment_status="paid",
        customer="cus_fake",
        subscription="sub_fake",
        customer_details=SimpleNamespace(email=email),
    )


def test_app_activates_subscription_from_checkout_session_id(client):
    client.post("/signup", data={"email": "paid@example.com", "password": "supersecret123"})
    with patch(
        "webapp.main.stripe.checkout.Session.retrieve",
        return_value=_fake_paid_session("paid@example.com"),
    ):
        resp = client.get("/app?session_id=cs_test_fake")
    assert resp.status_code == 200
    assert "Trova un affare" in resp.text  # dashboard, not the subscribe page


def test_app_ignores_session_id_for_a_different_email(client):
    client.post("/signup", data={"email": "mismatch@example.com", "password": "supersecret123"})
    with patch(
        "webapp.main.stripe.checkout.Session.retrieve",
        return_value=_fake_paid_session("someone-else@example.com"),
    ):
        resp = client.get("/app?session_id=cs_test_fake")
    assert resp.status_code == 200
    assert "Abbonati" in resp.text  # still locked


def test_language_switcher_avoids_the_post_only_search_path(client, monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    client.post("/signup", data={"email": "langswitch@example.com", "password": "supersecret123"})

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "langswitch@example.com").first()
        user.subscription_status = "active"
        db.commit()
    finally:
        db.close()

    resp = client.post(
        "/app/search", data={"query": "bici", "location": "Roma", "source": "vinted"}
    )
    assert resp.status_code == 200
    assert 'href="/app/search?lang=' not in resp.text
    assert 'href="/app?lang=en"' in resp.text


def _make_user(email: str) -> int:
    db = SessionLocal()
    try:
        user = User(email=email, password_hash=hash_password("supersecret123"))
        db.add(user)
        db.commit()
        db.refresh(user)
        return user.id
    finally:
        db.close()


def test_try_consume_search_allows_up_to_the_monthly_limit_then_blocks():
    user_id = _make_user("limits@example.com")
    for _ in range(MONTHLY_SEARCH_LIMIT):
        assert try_consume_search(user_id) is True
    assert try_consume_search(user_id) is False


def test_try_consume_search_counts_are_per_user():
    user_a = _make_user("usera@example.com")
    user_b = _make_user("userb@example.com")
    for _ in range(MONTHLY_SEARCH_LIMIT):
        try_consume_search(user_a)
    assert try_consume_search(user_a) is False
    assert try_consume_search(user_b) is True


def test_early_access_signup_stores_application(client):
    resp = client.post(
        "/api/early-access",
        json={
            "email": "waitlist1@example.com",
            "country": "Italy",
            "category": "bikes",
            "frequency": "monthly",
            "selected-profile": "pro",
            "day-one-trigger": "Finding a road bike under budget",
            "consent": "on",
        },
    )
    assert resp.status_code == 200
    assert resp.json() == {"ok": True}

    db = SessionLocal()
    try:
        saved = (
            db.query(EarlyAccessSignup)
            .filter(EarlyAccessSignup.email == "waitlist1@example.com")
            .one()
        )
        assert saved.country == "Italy"
        assert saved.category == "bikes"
        assert saved.selected_profile == "pro"
    finally:
        db.close()


def test_early_access_signup_rejects_missing_required_fields(client):
    resp = client.post(
        "/api/early-access",
        json={"email": "incomplete@example.com", "country": "", "category": ""},
    )
    assert resp.status_code == 400

    db = SessionLocal()
    try:
        assert (
            db.query(EarlyAccessSignup)
            .filter(EarlyAccessSignup.email == "incomplete@example.com")
            .first()
            is None
        )
    finally:
        db.close()


def test_early_access_signup_triggers_notification(client):
    with patch("webapp.main.notify_new_signup") as mock_notify:
        resp = client.post(
            "/api/early-access",
            json={"email": "notify-me@example.com", "country": "France", "category": "photo"},
        )
    assert resp.status_code == 200
    mock_notify.assert_called_once_with("notify-me@example.com", "France", "photo")


def test_early_access_signup_rejects_invalid_json(client):
    resp = client.post(
        "/api/early-access",
        content=b"not json",
        headers={"Content-Type": "application/json"},
    )
    assert resp.status_code == 400
