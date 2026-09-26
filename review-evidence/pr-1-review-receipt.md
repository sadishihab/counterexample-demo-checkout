PR Review Receipt — feat: support stacked coupons (closes #42)
Repo: counterexample-demo-checkout · Branch: feature/stacked-coupons · Issue: docs/ISSUE-42.md

Extracted Claims
ID | Claim | Source
claim-1 | Percent coupon applies to the amount remaining after the fixed discount, not the original subtotal | ISSUE-42 requirement 2
claim-2 | Order total never goes below 0.00 | ISSUE-42 requirement 3
claim-3 | Two coupons of the same kind raises ValueError | ISSUE-42 requirement 4
claim-4 | Result is independent of coupon list order | ISSUE-42 requirement 1 + PR docstring
claim-5 | Existing single-coupon and no-coupon call sites still work | ISSUE-42 "Notes" / backward compat

Verdicts

claim-1 — FALSIFIED
Adversarial test: subtotal=200, fixed=10, percent=10%.
Issue requirement 2 says percent applies to the post-fixed amount (190 → result 171.00).
Actual result: 170.00
The implementation in checkout/pricing.py does:
total -= subtotal * percent_coupons[0].value / Decimal("100")
subtotal is the original 200, not the total after the fixed deduction. The variable should be total on that line.
FAILED test_claim1_...::test_percent_coupon_applies_to_post_fixed_subtotal
AssertionError: Expected 171.00 (percent applied to post-fixed 190), got 170.00.

claim-2 — FALSIFIED
Adversarial test: subtotal=10, fixed coupon=50 (larger than subtotal).
Actual result: −40.00
The old max(total, ZERO) floor clamp was deleted in the PR and never replaced. Any fixed coupon exceeding the subtotal returns a negative total.
FAILED test_claim2_...::test_fixed_coupon_exceeds_subtotal
AssertionError: Order total went below zero: -40.00
assert Decimal('-40.00') >= Decimal('0.00')
(A 100% percent coupon accidentally returns 0.00 because the math cancels exactly — that sub-case passes.)

claim-3 — HELD
Two fixed coupons → ValueError. Two percent coupons → ValueError. Mixed cases (2 fixed + 1 percent, 3 fixed) → all ValueError. 5/5 adversarial tests passed.
This does not prove correctness in general, but no counterexample was found.

claim-4 — FALSIFIED
Adversarial test: subtotal=200, fixed=10, percent=10%.
Both [fixed, percent] and [percent, fixed] orderings return 170.00, so the two orderings agree with each other — but ISSUE-42 requires 171.00 (percent applied to the post-fixed remainder).
Order-independence around an incorrect value is not considered holding: this is the same root bug as claim-1, not independent confirmation of correctness.

claim-5 — FALSIFIED
Adversarial test: calling the new function with the old convention calculate_total(items, coupon_object) (a bare Coupon, not a list).
Actual result: TypeError: 'Coupon' object is not iterable
The guard coupons = coupons or [] passes a truthy Coupon object through unchanged; the subsequent list-comprehension on line 54 of checkout/pricing.py tries to iterate it and crashes.
FAILED test_claim5_...::test_bare_fixed_coupon_object_old_convention
TypeError: 'Coupon' object is not iterable  (checkout/pricing.py:54)
FAILED test_claim5_...::test_bare_percent_coupon_object_old_convention
TypeError: 'Coupon' object is not iterable  (checkout/pricing.py:54)

Summary
Claim | Verdict | Severity
Percent applies to post-fixed amount | FALSIFIED | Correct math, wrong implementation
Total never below 0.00 | FALSIFIED | Floor clamp deleted, not replaced
Duplicate kind raises ValueError | HELD | —
Order-independent result | FALSIFIED | Holds only if you don't check against the spec value — same bug as claim-1
Backward compat with bare Coupon arg | FALSIFIED | Silent breaking change for all existing callers

4 of 5 claims are falsified with real failing tests; only claim-3 (duplicate-kind raises ValueError) holds. The PR should not be merged as-is.
