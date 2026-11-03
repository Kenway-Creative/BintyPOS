# BintyPOS status

Version: **0.2.26** — atomic demo staff/device read guard
Date: 2026-11-03
Canonical: Kenway-Creative/BintyPOS · main
Rollback baseline: `4c1fed0f9d175e56b7207dc5571e6573fd1c2832`

## 0.2.26 checkpoint
- Added trusted Python-only atomic dual-capability read guard, requiring staff and registered device scopes for the same venue/outlet. Five regressions cover persistence, forgery/isolation, rotation/revocation, staff revocation and expiry. No HTTP/device pairing, real login or payments. CI verification pending.
- Rollback: `b2173f9cbc0d601aad07d4fd868dc34026377310`. Next: verify CI and define secure staff/device provisioning and TLS before any browser or write API.

## 0.2.25 checkpoint
- Added trusted-only persistent venue/outlet device capability registry, hashed tokens, expiry, rotation and revocation; five tests added. Device token does NOT authenticate a human or authorise an HTTP/checkout operation. Full CI verification pending.
- Rollback baseline: `79e8fa10fc78b31478c0e9bf578a5bc85b346407`. Next: combine verified staff and device binding in a guarded read-only operation; define secure pairing and TLS requirements before browser or writable routes.

## 0.2.24 checkpoint
- Read-only loopback HTTP staff probe now rejects Origin-bearing and cross-site/same-site Fetch Metadata requests before credential checks. Two new regressions; CI verification pending. This intentionally blocks browser integration, not a general CSRF or DNS rebinding solution.
- Rollback baseline: `91b7498f46fd3d7eb20a2f7472fa31298dec793e`. Next: verified staff/device provisioning and TLS threat model; no real payments.

## 0.2.23 checkpoint
- Strict single Host header matching loopback hostname and actual bound port; hostile and duplicate Host requests rejected before bearer verification. Two new HTTP regression tests. CI pending.
- Rollback baseline: 7bedbd6f902afc7b05c159e124d87fc6fd302498. Next: staff/device provisioning and TLS threat model; no public listener or real payments.

## 0.2.22 checkpoint
- Reject duplicate and oversized Authorization headers in loopback staff probe; add negative HTTP regressions. Full CI must be verified after commit. No login/TLS/payment changes.
- Rollback: `d7a4dfa75f7a05a45ff53ff1783cc30c5a858c04`. Next: authenticated human/device provisioning threat model, then guarded back-office API.

## 0.2.21 checkpoint
- Added opt-in loopback-only read-only staff access probe; no public HTTP, provisioning route, stock write or payment. Five new HTTP regression cases; GitHub Actions verification pending.
- Rollback: `436f2b2db19837410f98f2284e5d51dd56c5d9fd`. Next: trusted login/device provisioning and transport security threat model before any writable back-office HTTP route.

## 0.2.20 checkpoint
- Provisioned demo staff bearer token persisted as digest, with expiry and trusted revocation. Protected callbacks atomically validate token, current staff membership and outlet policy inside a SQLite writer transaction.
- Eight isolated tests passed locally using a compatibility copy of the existing staff directory/policy; full repository CI remains to be confirmed. No HTTP, verified human login, browser wiring or real payments.
- Implementation rollback: `1f6a2c3888700dafbb2ab1a70b08570696196706`. Next: a narrow authenticated HTTP endpoint only after provisioning/identity and request-boundary threat model.

## 0.2.19 checkpoint
- Added `GuardedStaffOperations.execute_trusted`: same SQLite writer transaction for membership lookup, outlet policy and trusted mutation. Five tests cover success, cross-outlet denial, revocation, rollback and competing revocation.
- This is NOT verified staff/device authentication; no HTTP, browser integration or live payments. All guarded writes must use the same database connection. CI result must be independently checked.
- Next: server-issued verified staff sessions bound to membership, then a deliberately narrow authenticated HTTP endpoint.

## 0.2.18 checkpoint
- Durable SQLite staff/outlet membership resolver, trusted-only enrol/revoke, fail-closed role projection and five regression tests. NOT verified staff authentication or atomic enforcement of business writes.
- Next: verify actual credentials server-side and enforce membership in the same writer transaction as back-office mutations. No public HTTP or live payments.

## 0.2.17 checkpoint
- Added pure fail-closed venue/outlet authorisation policy in `src/outlet_permissions.py` and 12 regression cases; separate trusted policy fixture, NOT verified login or integrated checkout enforcement.
- Local isolated policy tests passed 12/12 on Python; repository-wide CI pending verification. Source commit `6e32b76d09d8d724df0a16c5f94e825055f8bfca`, tests commit `fb1395a3e0b7e543e470db0250e8f4130e2b7e31`. Rollback baseline `9e33cf1331c3cd73b6bb48bbc90145001fd5d147`.
- Next: trusted principal resolution backed by durable staff/outlet memberships, then enforce policy within existing SQLite transaction boundary; no public HTTP or live payments.

## 0.2.16 checkpoint
- Added append-only mock reconciliation review decisions with venue-scoped lookup, durable SQLite history and idempotent request keys.
- Actor names are not authenticated; no automatic resolution or provider calls. Regression tests added; CI pending verification.
- Implementation commit: `f2c1bdf4f3dddb3c29bff8326408a0593f225411`; rollback baseline: `f1430fd2da176c27f34e41e0f155cb671a0b86f5`.
- Benchmark: Square payment retrieval/reconciliation can rely on real provider status; BintyPOS records only human mock notes. https://developer.squareup.com/docs/payments-api/overview

## 0.2.15 checkpoint
- Added trusted-only `MockReconciliationOutbox.snapshot_pending(venue)`: persistent, idempotent, venue-scoped snapshots of ambiguous mock orders. No dispatch, gateway calls, automatic resolution or payment movement.
- Added regression tests for restart, replay, isolation and unchanged stock/order status.
- Implementation commit: `d170e41832d5183556bcabda279a15a41c820fc6`; CI for this version pending independent verification. Rollback: `c3fa0a6f76b9f10fff828f77b635a5b69e4694f1`.
- Benchmark: Square Payments API supports querying payment state and idempotent payment operations; this prototype only retains unresolved mock records. https://developer.squareup.com/docs/payments-api/overview

## 0.2.14 checkpoint
- `ScopedDemoCheckout` validates capabilities and performs each protected operation within one SQLite writer transaction. Nested service calls use savepoints on the same connection.
- Added revocation concurrency and nested-savepoint rollback tests; CI verification pending.
- Rollback baseline: `249d7d07746c4501229ed5a03a363509a9aadb9e`. No release tag.
- Square benchmark: scoped credential revocation and least privilege; BintyPOS only serialises local demo token checks, without OAuth or human login.

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
- Facade validation and mutation are serialised in one SQLite writer transaction; internal trusted service methods still bypass the facade. Underlying internal service methods remain accessible to trusted Python code and bypass this facade.
- Browser demo remains separate from SQLite. Orphan holds and ambiguous mock outcomes still need transactional recovery/outbox.
- Dojo remains mandatory for planned initial payments pending sandbox validation; no real payment or Spektrix payment integration.

## Next bounded feature
**0.2.24 — trusted provisioning and transport security design**, followed by an authenticated HTTP boundary. No live gateway.

## Market comparison
Square's OAuth model supports scoped, short-lived/revocable access tokens and recommends least privilege. BintyPOS only demonstrates local hashed bearer capabilities for venue-bound checkout fixtures, not OAuth, staff login or equivalent security: https://developer.squareup.com/docs/auth and https://developer.squareup.com/docs/oauth-api/best-practices
