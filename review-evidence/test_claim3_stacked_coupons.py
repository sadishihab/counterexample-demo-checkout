"""Adversarial tests for claim-3: two coupons of the same kind raises ValueError."""
import pytest
from decimal import Decimal
from checkout.pricing import LineItem, Coupon, calculate_total

ITEMS = [LineItem(name="widget", unit_price=Decimal("100.00"), qty=1)]


def test_two_fixed_coupons_raises():
    """Two fixed coupons => should raise ValueError."""
    coupons = [
        Coupon(code="FIXED1", kind="fixed", value=Decimal("5.00")),
        Coupon(code="FIXED2", kind="fixed", value=Decimal("10.00")),
    ]
    with pytest.raises(ValueError):
        calculate_total(ITEMS, coupons)


def test_two_percent_coupons_raises():
    """Two percent coupons => should raise ValueError."""
    coupons = [
        Coupon(code="PCT1", kind="percent", value=Decimal("10")),
        Coupon(code="PCT2", kind="percent", value=Decimal("5")),
    ]
    with pytest.raises(ValueError):
        calculate_total(ITEMS, coupons)


def test_two_fixed_one_percent_raises():
    """Adversarial: 2 fixed + 1 percent => should raise ValueError (two fixed coupons)."""
    coupons = [
        Coupon(code="FIXED1", kind="fixed", value=Decimal("5.00")),
        Coupon(code="FIXED2", kind="fixed", value=Decimal("10.00")),
        Coupon(code="PCT1",   kind="percent", value=Decimal("10")),
    ]
    with pytest.raises(ValueError):
        calculate_total(ITEMS, coupons)


def test_one_fixed_two_percent_raises():
    """Adversarial: 1 fixed + 2 percent => should raise ValueError (two percent coupons)."""
    coupons = [
        Coupon(code="FIXED1", kind="fixed", value=Decimal("5.00")),
        Coupon(code="PCT1",   kind="percent", value=Decimal("10")),
        Coupon(code="PCT2",   kind="percent", value=Decimal("5")),
    ]
    with pytest.raises(ValueError):
        calculate_total(ITEMS, coupons)


def test_three_fixed_coupons_raises():
    """Adversarial: 3 fixed coupons => should raise ValueError."""
    coupons = [
        Coupon(code="FIXED1", kind="fixed", value=Decimal("5.00")),
        Coupon(code="FIXED2", kind="fixed", value=Decimal("10.00")),
        Coupon(code="FIXED3", kind="fixed", value=Decimal("3.00")),
    ]
    with pytest.raises(ValueError):
        calculate_total(ITEMS, coupons)
