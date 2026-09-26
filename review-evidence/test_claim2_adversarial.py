"""Adversarial test for claim-2:
'The order total never goes below 0.00, even when combined coupon
discounts exceed the subtotal.'
"""
from decimal import Decimal
import pytest
from checkout.pricing import LineItem, Coupon, calculate_total

ITEM_10 = [LineItem(name="widget", unit_price=Decimal("10.00"), qty=1)]


def test_fixed_coupon_exceeds_subtotal():
    """subtotal=10, fixed coupon=50 → should be clamped to 0.00, not -40.00"""
    coupons = [Coupon(code="BIG50", kind="fixed", value=Decimal("50"))]
    total = calculate_total(ITEM_10, coupons)
    assert total >= Decimal("0.00"), (
        f"Order total went below zero: {total}"
    )


def test_percent_coupon_100_percent():
    """subtotal=10, percent coupon=100% → should be 0.00, not -0.00 or negative"""
    coupons = [Coupon(code="FREE100", kind="percent", value=Decimal("100"))]
    total = calculate_total(ITEM_10, coupons)
    assert total >= Decimal("0.00"), (
        f"Order total went below zero: {total}"
    )
