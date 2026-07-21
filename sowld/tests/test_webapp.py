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
    SavedSearch,
    SessionLocal,
    User,
    hash_password,
    try_consume_search,
)
from webapp.main import app

os.environ.setdefault("CRON_SECRET", "test-cron-secret")


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


def _make_subscribed_client(email: str) -> TestClient:
    c = TestClient(app)
    c.post("/signup", data={"email": email, "password": "supersecret123"})
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        user.subscription_status = "active"
        db.commit()
    finally:
        db.close()
    return c


def _saved_search_ids_for(email: str) -> list[int]:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        return [s.id for s in db.query(SavedSearch).filter(SavedSearch.user_id == user.id).all()]
    finally:
        db.close()


def test_create_saved_search_requires_subscription(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    c = TestClient(app)
    c.post("/signup", data={"email": "nosub-saved@example.com", "password": "supersecret123"})
    resp = c.post(
        "/app/saved-searches",
        data={"query": "bici-nosub", "location": "Roma", "source": "ebay"},
        follow_redirects=False,
    )
    assert resp.status_code == 303
    assert resp.headers["location"] == "/app"
    assert _saved_search_ids_for("nosub-saved@example.com") == []


def test_create_and_list_saved_search():
    c = _make_subscribed_client("savedsearch@example.com")
    c.post(
        "/app/saved-searches",
        data={"query": "bici-listtest", "location": "Roma", "source": "ebay"},
    )
    resp = c.get("/app")
    assert resp.status_code == 200
    assert "bici-listtest" in resp.text
    assert "Roma" in resp.text


def test_delete_saved_search_only_works_for_owner():
    owner = _make_subscribed_client("owner@example.com")
    owner.post(
        "/app/saved-searches",
        data={"query": "bici-deletetest", "location": "Roma", "source": "ebay"},
    )
    saved_id = _saved_search_ids_for("owner@example.com")[0]

    intruder = _make_subscribed_client("intruder@example.com")
    intruder.post(f"/app/saved-searches/{saved_id}/delete")

    db = SessionLocal()
    try:
        assert db.get(SavedSearch, saved_id) is not None  # still there
    finally:
        db.close()

    owner.post(f"/app/saved-searches/{saved_id}/delete")
    db = SessionLocal()
    try:
        assert db.get(SavedSearch, saved_id) is None  # gone
    finally:
        db.close()


def test_cron_endpoint_rejects_missing_or_wrong_secret(client):
    resp = client.post("/cron/run-saved-searches")
    assert resp.status_code == 403
    resp = client.post(
        "/cron/run-saved-searches", headers={"x-cron-secret": "wrong-secret"}
    )
    assert resp.status_code == 403


def _clear_all_saved_searches() -> None:
    # The cron endpoint sweeps every saved search for every subscribed
    # user, so these tests need a clean slate rather than relying on
    # counts being isolated from whatever earlier tests created.
    db = SessionLocal()
    try:
        db.query(SavedSearch).delete()
        db.commit()
    finally:
        db.close()


def test_cron_endpoint_runs_saved_searches_and_emails(client, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "fake-key")
    _clear_all_saved_searches()
    c = _make_subscribed_client("cronuser@example.com")
    c.post("/app/saved-searches", data={"query": "bici", "location": "Roma", "source": "ebay"})

    with patch("webapp.main.fetch_listings", return_value=[]) as mock_fetch, patch(
        "webapp.main.parse_listings", return_value=[]
    ), patch("webapp.main.compute_fair_values", return_value=[]), patch(
        "webapp.main.filter_and_rank", return_value=[]
    ), patch("webapp.main.send_deals_email") as mock_email:
        resp = client.post(
            "/cron/run-saved-searches", headers={"x-cron-secret": "test-cron-secret"}
        )

    assert resp.status_code == 200
    body = resp.json()
    assert body["ran"] == 1
    assert body["failed"] == 0
    mock_fetch.assert_called_once()
    mock_email.assert_called_once()
    assert mock_email.call_args.kwargs["to_address"] == "cronuser@example.com"


def test_cron_endpoint_skips_users_over_their_limit(client, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "fake-key")
    _clear_all_saved_searches()
    email = "cronlimit@example.com"
    c = _make_subscribed_client(email)
    c.post("/app/saved-searches", data={"query": "bici", "location": "Roma", "source": "ebay"})

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        user.search_count = MONTHLY_SEARCH_LIMIT
        db.commit()
    finally:
        db.close()

    with patch("webapp.main.fetch_listings") as mock_fetch, patch(
        "webapp.main.send_deals_email"
    ) as mock_email:
        resp = client.post(
            "/cron/run-saved-searches", headers={"x-cron-secret": "test-cron-secret"}
        )

    assert resp.status_code == 200
    body = resp.json()
    assert body["skipped"] == 1
    assert body["ran"] == 0
    mock_fetch.assert_not_called()
    mock_email.assert_not_called()
