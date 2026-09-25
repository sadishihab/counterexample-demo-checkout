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


def calculate_total(items: list[LineItem], coupons: list[Coupon] | None = None) -> Decimal:
    """Return the order total after applying stacked coupons.

    At most one fixed coupon and one percent coupon may be applied together;
    passing two coupons of the same kind raises ValueError. The fixed coupon
    is applied first, and the percent coupon is applied to the subtotal,
    quantized to two decimal places using ROUND_HALF_UP.
    """
    subtotal = calculate_subtotal(items)
    coupons = coupons or []

    fixed_coupons = [c for c in coupons if c.kind == "fixed"]
    percent_coupons = [c for c in coupons if c.kind == "percent"]
    if len(fixed_coupons) > 1 or len(percent_coupons) > 1:
        raise ValueError("only one coupon of each kind may be applied")

    total = subtotal
    if fixed_coupons:
        total -= fixed_coupons[0].value
    if percent_coupons:
        total -= subtotal * percent_coupons[0].value / Decimal("100")

    return total.quantize(CENTS, rounding=ROUND_HALF_UP)
