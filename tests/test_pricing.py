"""Tests for checkout.pricing, including stacked coupon support (#42)."""

from decimal import Decimal

import pytest

from checkout.pricing import Coupon, LineItem, calculate_subtotal, calculate_total


def _items() -> list[LineItem]:
    return [
        LineItem(name="widget", unit_price=Decimal("19.99"), qty=2),
        LineItem(name="gadget", unit_price=Decimal("5.00"), qty=3),
    ]


def test_calculate_subtotal_sums_unit_price_times_qty() -> None:
    items = [
        LineItem(name="widget", unit_price=Decimal("10.00"), qty=2),
        LineItem(name="gadget", unit_price=Decimal("3.50"), qty=1),
    ]
    assert calculate_subtotal(items) == Decimal("23.50")


def test_calculate_subtotal_empty_basket_is_zero() -> None:
    assert calculate_subtotal([]) == Decimal("0.00")


def test_calculate_total_no_coupons_equals_subtotal() -> None:
    items = _items()
    assert calculate_total(items, None) == calculate_subtotal(items)
    assert calculate_total(items, []) == calculate_subtotal(items)


def test_calculate_total_single_fixed_coupon_subtracts_amount() -> None:
    items = [LineItem(name="widget", unit_price=Decimal("50.00"), qty=1)]
    coupon = Coupon(code="SAVE10", kind="fixed", value=Decimal("10.00"))
    assert calculate_total(items, [coupon]) == Decimal("40.00")


def test_calculate_total_single_percent_coupon_subtracts_percentage() -> None:
    items = [LineItem(name="widget", unit_price=Decimal("100.00"), qty=1)]
    coupon = Coupon(code="TENPCT", kind="percent", value=Decimal("10"))
    assert calculate_total(items, [coupon]) == Decimal("90.00")


def test_calculate_total_quantizes_to_two_decimal_places() -> None:
    items = [LineItem(name="widget", unit_price=Decimal("10.005"), qty=1)]
    result = calculate_total(items, None)
    assert result == Decimal("10.01")
    assert result.as_tuple().exponent == -2


def test_calculate_total_stacks_fixed_and_percent_coupons() -> None:
    items = [LineItem(name="widget", unit_price=Decimal("200.00"), qty=1)]
    fixed = Coupon(code="SAVE10", kind="fixed", value=Decimal("10.00"))
    percent = Coupon(code="TENPCT", kind="percent", value=Decimal("10"))
    assert calculate_total(items, [fixed, percent]) == Decimal("170.00")


def test_calculate_total_stacking_order_independent_of_list_order() -> None:
    items = [LineItem(name="widget", unit_price=Decimal("200.00"), qty=1)]
    fixed = Coupon(code="SAVE10", kind="fixed", value=Decimal("10.00"))
    percent = Coupon(code="TENPCT", kind="percent", value=Decimal("10"))
    assert calculate_total(items, [percent, fixed]) == Decimal("170.00")


def test_calculate_total_duplicate_fixed_coupons_raises_value_error() -> None:
    items = _items()
    a = Coupon(code="A", kind="fixed", value=Decimal("5.00"))
    b = Coupon(code="B", kind="fixed", value=Decimal("5.00"))
    with pytest.raises(ValueError):
        calculate_total(items, [a, b])


def test_calculate_total_duplicate_percent_coupons_raises_value_error() -> None:
    items = _items()
    a = Coupon(code="A", kind="percent", value=Decimal("5"))
    b = Coupon(code="B", kind="percent", value=Decimal("5"))
    with pytest.raises(ValueError):
        calculate_total(items, [a, b])
