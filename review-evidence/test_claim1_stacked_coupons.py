"""Adversarial test for claim-1:
'The fixed coupon is applied first, and the percent coupon is applied to the
amount remaining AFTER the fixed discount (i.e., percent is applied to
subtotal - fixed, not to the original subtotal).'

Edge case: subtotal=200, fixed=10, percent=10%
  - If percent applies to POST-FIXED amount (190): total = 200 - 10 - 19 = 171  (claim HOLDS)
  - If percent applies to ORIGINAL subtotal (200): total = 200 - 10 - 20 = 170  (claim FALSIFIED)
"""
from decimal import Decimal
import pytest
from checkout.pricing import LineItem, Coupon, calculate_total


def test_percent_coupon_applies_to_post_fixed_subtotal():
    """Claim-1: percent coupon must apply to (subtotal - fixed), not original subtotal."""
    items = [LineItem(name="Widget", unit_price=Decimal("200.00"), qty=1)]
    fixed_coupon = Coupon(code="FIXED10", kind="fixed", value=Decimal("10"))
    percent_coupon = Coupon(code="PCT10", kind="percent", value=Decimal("10"))

    total = calculate_total(items, [fixed_coupon, percent_coupon])

    # If percent is applied to post-fixed amount (190), result should be 171.00
    # If percent is applied to original subtotal (200), result would be 170.00
    assert total == Decimal("171.00"), (
        f"Expected 171.00 (percent applied to post-fixed 190), got {total}. "
        "This means percent was applied to the original subtotal, not the post-fixed amount."
    )
