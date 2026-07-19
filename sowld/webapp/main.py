"""Sowld web app: signup, Stripe subscription, and a gated search page.

Wraps the existing sowld/ package (fetch -> parse -> valuation -> scoring)
behind a login + paid-subscription wall, so it can be linked to from the
Framer marketing site (Part A) as a real "go to the platform" URL, instead
of being a script someone has to run themselves.
"""

from __future__ import annotations

import os
from pathlib import Path

import stripe
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from sowld.fetch import BETA_SOURCES, DEFAULT_SOURCE, SOURCES, fetch_listings
from sowld.parse import parse_listings
from sowld.scoring import DEFAULT_THRESHOLD, filter_and_rank
from sowld.valuation import compute_fair_values

from .auth import get_current_user
from .auth import login as start_session
from .auth import logout as end_session
from .billing import create_billing_portal_session, create_checkout_session, is_configured
from .db import SessionLocal, User, hash_password, init_db, try_consume_search, verify_password
from .i18n import LANGUAGES, get_translator, resolve_language

app = FastAPI(title="Sowld")
app.add_middleware(
    SessionMiddleware,
    secret_key=os.environ.get("SESSION_SECRET_KEY", "dev-secret-change-me"),
)
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))

init_db()


def _base_context(request: Request) -> dict:
    lang = resolve_language(request)
    return {"lang": lang, "languages": LANGUAGES, "t": get_translator(lang)}


@app.get("/", response_class=HTMLResponse)
def landing(request: Request):
    return templates.TemplateResponse(
        request,
        "landing.html",
        {**_base_context(request), "user": get_current_user(request)},
    )


@app.get("/signup", response_class=HTMLResponse)
def signup_form(request: Request):
    return templates.TemplateResponse(
        request, "signup.html", {**_base_context(request), "user": None, "error": None}
    )


@app.post("/signup")
def signup_submit(request: Request, email: str = Form(...), password: str = Form(...)):
    ctx = _base_context(request)
    db = SessionLocal()
    try:
        if db.query(User).filter(User.email == email).first():
            return templates.TemplateResponse(
                request,
                "signup.html",
                {**ctx, "user": None, "error": ctx["t"]("signup.error_duplicate")},
                status_code=400,
            )
        user = User(email=email, password_hash=hash_password(password))
        db.add(user)
        db.commit()
        db.refresh(user)
        start_session(request, user)
    finally:
        db.close()
    return RedirectResponse("/app", status_code=303)


@app.get("/login", response_class=HTMLResponse)
def login_form(request: Request):
    return templates.TemplateResponse(
        request, "login.html", {**_base_context(request), "user": None, "error": None}
    )


@app.post("/login")
def login_submit(request: Request, email: str = Form(...), password: str = Form(...)):
    ctx = _base_context(request)
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user or not verify_password(password, user.password_hash):
            return templates.TemplateResponse(
                request,
                "login.html",
                {**ctx, "user": None, "error": ctx["t"]("login.error_invalid")},
                status_code=400,
            )
        start_session(request, user)
    finally:
        db.close()
    return RedirectResponse("/app", status_code=303)


@app.post("/logout")
def logout_submit(request: Request):
    end_session(request)
    return RedirectResponse("/", status_code=303)


@app.get("/billing/checkout")
def billing_checkout(request: Request):
    ctx = _base_context(request)
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=303)
    if not is_configured():
        return HTMLResponse(ctx["t"]("error.stripe_not_configured"), status_code=503)
    base_url = str(request.base_url).rstrip("/")
    url = create_checkout_session(
        customer_email=user.email,
        success_url=f"{base_url}/app?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{base_url}/app",
    )
    return RedirectResponse(url, status_code=303)


def _activate_from_checkout_session(user_id: int, session_id: str) -> bool:
    """Confirm a checkout session directly with Stripe and activate the
    subscription immediately, instead of waiting on the webhook.

    The webhook (below) is still the source of truth for renewals and
    cancellations, but relying on it alone for this first activation is
    fragile: Render's free tier can spin an idle instance down, and a
    delayed wake-up can make Stripe's webhook delivery time out.
    """
    try:
        session = stripe.checkout.Session.retrieve(session_id)
    except stripe.error.StripeError:
        return False
    if session.payment_status != "paid":
        return False

    db = SessionLocal()
    try:
        db_user = db.get(User, user_id)
        details_email = session.customer_details.email if session.customer_details else None
        if not db_user or details_email != db_user.email:
            return False
        db_user.stripe_customer_id = session.customer
        db_user.stripe_subscription_id = session.subscription
        db_user.subscription_status = "active"
        db.commit()
        return True
    finally:
        db.close()


@app.get("/billing/portal")
def billing_portal(request: Request):
    user = get_current_user(request)
    if not user or not user.stripe_customer_id:
        return RedirectResponse("/app", status_code=303)
    base_url = str(request.base_url).rstrip("/")
    url = create_billing_portal_session(user.stripe_customer_id, return_url=f"{base_url}/app")
    return RedirectResponse(url, status_code=303)


@app.post("/webhooks/stripe")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")
    webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except (ValueError, stripe.error.SignatureVerificationError):
        return HTMLResponse("invalid signature", status_code=400)

    db = SessionLocal()
    try:
        data = event["data"]["object"]

        if event["type"] == "checkout.session.completed":
            email = (data.get("customer_details") or {}).get("email") or data.get("customer_email")
            user = db.query(User).filter(User.email == email).first() if email else None
            if user:
                user.stripe_customer_id = data.get("customer")
                user.stripe_subscription_id = data.get("subscription")
                user.subscription_status = "active"
                db.commit()

        elif event["type"] in ("customer.subscription.updated", "customer.subscription.deleted"):
            user = db.query(User).filter(User.stripe_customer_id == data.get("customer")).first()
            if user:
                user.subscription_status = "active" if data.get("status") == "active" else "canceled"
                db.commit()
    finally:
        db.close()

    return {"received": True}


@app.get("/app", response_class=HTMLResponse)
def app_home(request: Request):
    ctx = _base_context(request)
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=303)

    session_id = request.query_params.get("session_id")
    if session_id and not user.is_subscribed:
        if _activate_from_checkout_session(user.id, session_id):
            user = get_current_user(request)

    if not user.is_subscribed:
        return templates.TemplateResponse(request, "subscribe.html", {**ctx, "user": user})
    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            **ctx,
            "user": user,
            "sources": sorted(SOURCES),
            "beta_sources": BETA_SOURCES,
            "source": DEFAULT_SOURCE,
            "results": None,
        },
    )


@app.post("/app/search", response_class=HTMLResponse)
def app_search(
    request: Request,
    query: str = Form(...),
    location: str = Form(...),
    source: str = Form(DEFAULT_SOURCE),
):
    ctx = _base_context(request)
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=303)
    if not user.is_subscribed:
        return RedirectResponse("/app", status_code=303)

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    error = None
    deals = []
    if not api_key:
        error = ctx["t"]("error.anthropic_not_configured")
    elif not try_consume_search(user.id):
        error = ctx["t"]("error.usage_limit_reached")
    else:
        try:
            listings = fetch_listings(query, location, source=source, max_results=40)
            parsed = parse_listings(listings, api_key=api_key)
            valued = compute_fair_values(parsed)
            deals = filter_and_rank(valued, threshold=DEFAULT_THRESHOLD)
        except Exception as exc:  # external marketplace/API call — surface, don't 500
            error = str(exc)

    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            **ctx,
            "user": user,
            "sources": sorted(SOURCES),
            "beta_sources": BETA_SOURCES,
            "results": deals,
            "query": query,
            "location": location,
            "source": source,
            "error": error,
        },
    )
