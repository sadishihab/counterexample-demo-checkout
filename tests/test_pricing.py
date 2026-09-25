"""Tests for checkout.pricing single-coupon behaviour."""

from decimal import Decimal

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


def test_calculate_total_no_coupon_equals_subtotal() -> None:
    items = _items()
    assert calculate_total(items, None) == calculate_subtotal(items)


def test_calculate_total_fixed_coupon_subtracts_amount() -> None:
    items = [LineItem(name="widget", unit_price=Decimal("50.00"), qty=1)]
    coupon = Coupon(code="SAVE10", kind="fixed", value=Decimal("10.00"))
    assert calculate_total(items, coupon) == Decimal("40.00")


def test_calculate_total_percent_coupon_subtracts_percentage() -> None:
    items = [LineItem(name="widget", unit_price=Decimal("100.00"), qty=1)]
    coupon = Coupon(code="TENPCT", kind="percent", value=Decimal("10"))
    assert calculate_total(items, coupon) == Decimal("90.00")


def test_calculate_total_fixed_coupon_larger_than_subtotal_clamps_to_zero() -> None:
    items = [LineItem(name="widget", unit_price=Decimal("10.00"), qty=1)]
    coupon = Coupon(code="BIG", kind="fixed", value=Decimal("50.00"))
    assert calculate_total(items, coupon) == Decimal("0.00")


def test_calculate_total_percent_coupon_of_100_clamps_to_zero() -> None:
    items = [LineItem(name="widget", unit_price=Decimal("25.00"), qty=1)]
    coupon = Coupon(code="FREE", kind="percent", value=Decimal("100"))
    assert calculate_total(items, coupon) == Decimal("0.00")


def test_calculate_total_quantizes_to_two_decimal_places() -> None:
    items = [LineItem(name="widget", unit_price=Decimal("10.005"), qty=1)]
    result = calculate_total(items, None)
    assert result == Decimal("10.01")
    assert result.as_tuple().exponent == -2
