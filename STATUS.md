# BintyPOS status

Version: **0.2.10** — trusted quote-bound SQLite reservation prototype
Date: 2026-11-02
Canonical: Kenway-Creative/BintyPOS · main
Rollback baseline (v0.2.9): `11f7def96b633c7573b06dde306de00373355a84`
Implementation commit: `f3afc3163bf53f2fe62620d4fa77c7b834a9753d`
Test commit: `5144b8d4e9d153ed003cad956da2eac3564e2f01`

## Implemented
- `src/trusted_checkout.py` extends internal SQLite reservations with persisted published-product fixtures and immutable quote snapshots (business, GBP-pence price, product version, recipe).
- Only product ID and quantity are accepted when creating a quote; price and ingredient demand are calculated from trusted stored product data.
- Quote acceptance verifies expected total, session fixture, expiry and published product/recipe versions.
- Reservation atomically verifies accepted quote, expiry, versions, checkout session fixture, available shared ingredient stock and idempotency, then persists the hold.
- One quote binds to one reservation key; competing independent SQLite connections serialize.
- The original browser till and QR demo are unchanged and continue using local in-memory reservations.

## Verification
- **14/14 new Python unit tests passed locally on Python 3.13.5** using `python -m unittest discover -s tests -p 'test_*.py' -v` in a local copy of the new source and unchanged SQLite adapter.
- `python -m py_compile src/trusted_checkout.py` passed.
- Exact Git blob SHA of tested source: `d00e8d311ca8c8791e8bee9d8903c38087f29b29`; committed source SHA matches. Tested tests blob: `5c981699fcf97f685299d2caa9a896b73604a4da`; committed test SHA matches.
- Existing 13 Python SQLite tests and 146 Node tests are unchanged, previously passed; **complete GitHub Actions run for this release is not independently confirmed**.
- GitHub Pages deploy/live browser/device status is not independently confirmed.

## Security and operational limitations
- Session ID is a caller-supplied test fixture, **not verified authentication**; `publish_product` is an internal fixture operation, not a secure manager console.
- Inherited direct-demand `reserve()` and `commit()` are trusted internal methods. Never expose to browsers. Commit does not verify payment.
- No HTTP server, production database architecture, live order ledger, VAT/tax/discount calculations, Dojo sandbox/live integration, webhook reconciliation or Spektrix integration.
- No real card payments. No production readiness claim.

## Next bounded feature
**0.2.11 — authenticated checkout identity and durable order/payment-state scaffold.** Add explicit verified actor/venue boundaries and state transitions for reserved, awaiting payment, confirmed, failed and released, with a mock provider only. Preserve future Dojo adapter separation; do not capture real money.

## Market comparison
Square Inventory API supports atomic inventory batches and idempotency; BintyPOS demonstrates transactionally safe accepted-quote recipe demand for one SQLite file, not Square-equivalent operations.
https://developer.squareup.com/docs/inventory-api/how-it-works
https://developer.squareup.com/reference/square/inventory-api/BatchChangeInventory
