# Issue #42: Support stacking coupons at checkout

## Summary

Currently `calculate_total` accepts at most one coupon. Customers are asking to be
able to combine a fixed-amount coupon with a percent-off coupon in the same order.

## Requirements

1. A customer may apply at most one fixed coupon and at most one percent coupon
   together.
2. The fixed coupon is applied first; the percent coupon applies to the amount
   remaining after the fixed discount.
3. The order total must never go below 0.00.
4. Applying two coupons of the same kind raises `ValueError`.

## Notes

Existing single-coupon checkouts should continue to work unchanged.
