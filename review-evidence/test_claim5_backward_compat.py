"""
Adversarial backward-compatibility tests for claim-5.

OLD signature: calculate_total(items, coupon: Coupon | None)
NEW signature: calculate_total(items, coupons: list[Coupon] | None = None)

We test:
  (a) calculate_total(items, None)        => subtotal (no discount)
  (b) calculate_total(items, [fixed])     => fixed discount applied
  (c) calculate_total(items, [percent])   => percent discount applied
  (d) CRITICAL: calculate_total(items, coupon_object)
      -- old callers passed a bare Coupon, not a list.
      -- The new code does `coupons or []` then iterates; a bare Coupon is
         a truthy non-None value, so `coupons or []` returns the Coupon itself,
         and the list-comprehensions iterate over its *characters* / fields.
         This should silently misbehave or crash.
"""

from decimal import Decimal
import pytest

# --- adjust sys.path so we can import from the repo root ---
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "checkout"))

from pricing import LineItem, Coupon, calculate_total, calculate_subtotal

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

ITEMS = [
    LineItem(name="Widget", unit_price=Decimal("10.00"), qty=3),   # 30.00
    LineItem(name="Gadget", unit_price=Decimal("5.50"),  qty=2),   # 11.00
]
SUBTOTAL = Decimal("41.00")

FIXED_COUPON   = Coupon(code="SAVE5",  kind="fixed",   value=Decimal("5.00"))
PERCENT_COUPON = Coupon(code="PCT10",  kind="percent",  value=Decimal("10"))


# ---------------------------------------------------------------------------
# (a) None coupon => no discount
# ---------------------------------------------------------------------------

def test_no_coupon_none():
    """calculate_total(items, None) must equal the subtotal."""
    result = calculate_total(ITEMS, None)
    assert result == SUBTOTAL, (
        f"Expected {SUBTOTAL}, got {result}. "
        "Passing None broke the no-discount path."
    )


# ---------------------------------------------------------------------------
# (b) Single fixed coupon in a list
# ---------------------------------------------------------------------------

def test_single_fixed_coupon_in_list():
    """calculate_total(items, [fixed_coupon]) must subtract the fixed amount."""
    expected = SUBTOTAL - FIXED_COUPON.value  # 36.00
    result = calculate_total(ITEMS, [FIXED_COUPON])
    assert result == expected, (
        f"Expected {expected}, got {result}. "
        "Single fixed coupon wrapped in list is broken."
    )


# ---------------------------------------------------------------------------
# (c) Single percent coupon in a list
# ---------------------------------------------------------------------------

def test_single_percent_coupon_in_list():
    """calculate_total(items, [percent_coupon]) must subtract the percentage."""
    discount  = (SUBTOTAL * PERCENT_COUPON.value / Decimal("100"))
    expected  = (SUBTOTAL - discount).quantize(Decimal("0.01"))
    result    = calculate_total(ITEMS, [PERCENT_COUPON])
    assert result == expected, (
        f"Expected {expected}, got {result}. "
        "Single percent coupon wrapped in list is broken."
    )


# ---------------------------------------------------------------------------
# (d) CRITICAL: bare Coupon object passed (old calling convention)
#     Old callers wrote: calculate_total(items, my_coupon)
#     With the new signature this is NOT a list, so the code
#     does `coupons or []` — since a Coupon is truthy it returns
#     the Coupon object itself, then iterates over it in list-comps
#     which will raise TypeError (Coupon is not iterable).
#     Either way (TypeError or wrong answer), backward compat is BROKEN.
# ---------------------------------------------------------------------------

def test_bare_fixed_coupon_object_old_convention():
    """
    OLD callers: calculate_total(items, coupon_object)  -- NOT a list.
    This MUST produce the correct discounted total to be backward-compatible.
    Expected: SUBTOTAL - 5.00 = 36.00
    """
    expected = SUBTOTAL - FIXED_COUPON.value  # 36.00
    # If this raises an exception the test fails (backward compat broken).
    # If it returns a wrong value the assert catches it.
    result = calculate_total(ITEMS, FIXED_COUPON)
    assert result == expected, (
        f"Expected {expected}, got {result}. "
        "Bare Coupon object (old convention) produces wrong result."
    )


def test_bare_percent_coupon_object_old_convention():
    """
    OLD callers: calculate_total(items, percent_coupon)  -- NOT a list.
    Must discount by 10% of subtotal.
    """
    discount = (SUBTOTAL * PERCENT_COUPON.value / Decimal("100"))
    expected = (SUBTOTAL - discount).quantize(Decimal("0.01"))
    result = calculate_total(ITEMS, PERCENT_COUPON)
    assert result == expected, (
        f"Expected {expected}, got {result}. "
        "Bare percent Coupon object (old convention) produces wrong result."
    )


def test_bare_none_is_still_no_discount():
    """
    Sanity: calculate_total(items) with no second arg must equal subtotal.
    (Tests default-argument path, not really old convention but confirming
    the default still works.)
    """
    result = calculate_total(ITEMS)
    assert result == SUBTOTAL, (
        f"Expected {SUBTOTAL}, got {result}. Default no-coupon path broken."
    )
