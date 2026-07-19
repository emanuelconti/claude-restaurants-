"""Stripe subscription integration.

Uses Stripe Checkout (a hosted payment page), so no card data ever touches
this server. Two moving parts: create_checkout_session() sends a new user
to pay, and the webhook handler in main.py reacts when Stripe tells us a
subscription started or ended.

Works against Stripe's TEST-mode keys with zero real charges — flip to
live keys only once you're ready to actually bill people.
"""

from __future__ import annotations

import os

import stripe

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY", "")
PRICE_ID = os.environ.get("STRIPE_PRICE_ID", "")


def is_configured() -> bool:
    return bool(os.environ.get("STRIPE_SECRET_KEY") and os.environ.get("STRIPE_PRICE_ID"))


def create_checkout_session(customer_email: str, success_url: str, cancel_url: str) -> str:
    session = stripe.checkout.Session.create(
        mode="subscription",
        payment_method_types=["card"],
        customer_email=customer_email,
        line_items=[{"price": PRICE_ID, "quantity": 1}],
        success_url=success_url,
        cancel_url=cancel_url,
    )
    return session.url


def create_billing_portal_session(stripe_customer_id: str, return_url: str) -> str:
    session = stripe.billing_portal.Session.create(customer=stripe_customer_id, return_url=return_url)
    return session.url
