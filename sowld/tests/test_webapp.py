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
