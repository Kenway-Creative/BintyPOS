# BintyPOS status

Version: **0.2.12** — scoped, revocable demo checkout identity facade
Date: 2026-11-03
Canonical: Kenway-Creative/BintyPOS · main
Rollback baseline: `4c1fed0f9d175e56b7207dc5571e6573fd1c2832`

## Implemented
- Added `src/checkout_identity.py`: SQLite-persisted random checkout capabilities, SHA-256 digest storage, expiry/revocation, venue binding and server-derived session IDs for staff and QR mock checkout.
- Narrow facade for quote, acceptance, order creation and status; staff-only mock cancellation. Checkout capability cannot authorise or confirm payment or directly commit inventory.
- Added 13 Python security/behaviour regression tests and proposed OpenAPI checkoutAuth boundary.

## Verification checkpoint
- Baseline GitHub Actions run 41549592450 succeeded on 2026-11-03 for v0.2.11: Node 147/147, Python 39/39 and Pages workflow step succeeded.
- v0.2.12 verification: see latest GitHub Actions run for the implementation commit; do not assume success from source publication. Local new-file Python compilation succeeded; complete suite must run on GitHub Actions.
- No independently verified public browser/device or operational API.

## Limitations and blockers
- Demo capability issuance is a **trusted fixture hook**, not staff login; it must not be exposed over HTTP. Possession of a token is sufficient for this prototype; no staff verification, device attestation, MFA, TLS or rate limiting.
- Token validation and mutation are separate transactions; revocation may race an already authorised operation. Underlying internal service methods remain accessible to trusted Python code and bypass this facade.
- Browser demo remains separate from SQLite. Orphan holds and ambiguous mock outcomes still need transactional recovery/outbox.
- Dojo remains mandatory for planned initial payments pending sandbox validation; no real payment or Spektrix payment integration.

## Next bounded feature
**0.2.13 — transactional recovery for orphaned order holds and ambiguous mock outcomes**, with deterministic retry, safe reconciliation and concurrency tests. No live gateway.

## Market comparison
Square's OAuth model supports scoped, short-lived/revocable access tokens and recommends least privilege. BintyPOS only demonstrates local hashed bearer capabilities for venue-bound checkout fixtures, not OAuth, staff login or equivalent security: https://developer.squareup.com/docs/auth and https://developer.squareup.com/docs/oauth-api/best-practices
