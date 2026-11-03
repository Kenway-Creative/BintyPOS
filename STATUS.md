# BintyPOS status

Version: **0.2.13** — deterministic mock order recovery inspection
Date: 2026-11-03
Canonical: Kenway-Creative/BintyPOS · main
Rollback baseline: `4c1fed0f9d175e56b7207dc5571e6573fd1c2832`

## 0.2.13 checkpoint
- Added `src/order_recovery.py` trusted-only atomic expiry/inspection of orphan holds and ambiguous simulated outcomes, plus four regression tests.
- Existing v0.2.12 CI success remains the baseline; v0.2.13 CI and Pages are **not yet verified** at documentation write time.
- Rollback baseline: `72314760e585fe2f873439baca80cff3833fa342`. No release tag.

## Implemented
- Added `src/checkout_identity.py`: SQLite-persisted random checkout capabilities, SHA-256 digest storage, expiry/revocation, venue binding and server-derived session IDs for staff and QR mock checkout.
- Narrow facade for quote, acceptance, order creation and status; staff-only mock cancellation. Checkout capability cannot authorise or confirm payment or directly commit inventory.
- Added 13 Python security/behaviour regression tests and proposed OpenAPI checkoutAuth boundary.

## Verification checkpoint
- Baseline GitHub Actions run 41549592450 succeeded on 2026-11-03 for v0.2.11: Node 147/147, Python 39/39 and Pages workflow step succeeded.
- **v0.2.12 GitHub Actions run 41556538336 succeeded** (2026-11-03): native Node 22 **148/148 tests**, Python 3.13 **52/52 tests**, and GitHub Pages deployment step succeeded. https://github.com/Kenway-Creative/BintyPOS/actions/runs/41556538336
- Initial run 41556510708 failed at the Node contract assertion; corrected escaped version/security regex in `7f2068c95e1283946c1b1c5dc4793d630a974b73`. The successful run verifies that repair.
- No independently verified public browser/device or operational API.

## Limitations and blockers
- Demo capability issuance is a **trusted fixture hook**, not staff login; it must not be exposed over HTTP. Possession of a token is sufficient for this prototype; no staff verification, device attestation, MFA, TLS or rate limiting.
- Token validation and mutation are separate transactions; revocation may race an already authorised operation. Underlying internal service methods remain accessible to trusted Python code and bypass this facade.
- Browser demo remains separate from SQLite. Orphan holds and ambiguous mock outcomes still need transactional recovery/outbox.
- Dojo remains mandatory for planned initial payments pending sandbox validation; no real payment or Spektrix payment integration.

## Next bounded feature
**0.2.14 — atomic checkout capability validation and mutation**, then durable outbox/reconciliation worker and verified human/device identity. No live gateway.

## Market comparison
Square's OAuth model supports scoped, short-lived/revocable access tokens and recommends least privilege. BintyPOS only demonstrates local hashed bearer capabilities for venue-bound checkout fixtures, not OAuth, staff login or equivalent security: https://developer.squareup.com/docs/auth and https://developer.squareup.com/docs/oauth-api/best-practices
