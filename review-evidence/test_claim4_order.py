"""Adversarial test for claim-4: order independence of stacked coupons."""
import sys
import os
sys.path.insert(0, "/home/sadi/projects/ibm-bob-2.0/counterexample-demo-checkout")

from decimal import Decimal
from checkout.pricing import LineItem, Coupon, calculate_total

ITEMS = [LineItem(name="widget", unit_price=Decimal("200.00"), qty=1)]
FIXED   = Coupon(code="FIXED10", kind="fixed",   value=Decimal("10"))
PERCENT = Coupon(code="PCT10",   kind="percent",  value=Decimal("10"))


def test_claim4_order_independence():
    """
    Adversarial test: subtotal=200, fixed=10, percent=10.

    If discounts were applied SEQUENTIALLY:
      [fixed, percent]: (200 - 10) * 0.90 = 171.00
      [percent, fixed]: (200 * 0.90) - 10 = 170.00  <-- different!

    The claim says both orderings must give the same total.
    """
    total_fixed_first   = calculate_total(ITEMS, [FIXED, PERCENT])
    total_percent_first = calculate_total(ITEMS, [PERCENT, FIXED])

    print(f"\n  [fixed, percent]  -> {total_fixed_first}")
    print(f"  [percent, fixed]  -> {total_percent_first}")

    assert total_fixed_first == total_percent_first, (
        f"Order matters! [fixed, percent]={total_fixed_first} "
        f"!= [percent, fixed]={total_percent_first}"
    )
