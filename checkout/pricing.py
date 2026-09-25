"""Checkout pricing: line items, a single coupon, and totals."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from typing import Literal

CENTS = Decimal("0.01")
ZERO = Decimal("0.00")


@dataclass(frozen=True)
class LineItem:
    """A single line item in a checkout basket."""

    name: str
    unit_price: Decimal
    qty: int


@dataclass(frozen=True)
class Coupon:
    """A discount coupon.

    `kind` is either "fixed" (subtract `value` currency units) or "percent"
    (subtract `value` percent of the subtotal).
    """

    code: str
    kind: Literal["fixed", "percent"]
    value: Decimal


def calculate_subtotal(items: list[LineItem]) -> Decimal:
    """Return the sum of unit_price * qty across all line items."""
    subtotal = ZERO
    for item in items:
        subtotal += item.unit_price * item.qty
    return subtotal


def calculate_total(items: list[LineItem], coupon: Coupon | None) -> Decimal:
    """Return the order total after applying at most one coupon.

    A fixed coupon subtracts its value directly from the subtotal. A percent
    coupon subtracts `subtotal * value / 100`. The result is clamped at
    Decimal("0.00") and quantized to two decimal places using ROUND_HALF_UP.
    """
    subtotal = calculate_subtotal(items)

    if coupon is None:
        discount = ZERO
    elif coupon.kind == "fixed":
        discount = coupon.value
    else:
        discount = subtotal * coupon.value / Decimal("100")

    total = subtotal - discount
    total = max(total, ZERO)
    return total.quantize(CENTS, rounding=ROUND_HALF_UP)
