## Current checkpoint — 2026-11-06 18:00 UTC
- v0.2.28 corrects misleading v0.2.8 header/footer by showing framework and browser-demo versions separately. Regression test: tests/version-label.test.cjs. The OpenAPI contract remains 0.2.27 (unchanged).
- Prior verified baseline: 42fe693734a9961f4d826a6b33be200ed556083d; push run 41964790621, job 127039189694, 13/13 steps successful including Node, Python and Pages deployment. This does NOT certify subsequent commits.
- New commits: index 093260257998d4bfa255e991d4e82e19b2dff2b3; regression a86dcd1cd435d7c023c8a69030b82dae1bd97b95. Current HEAD CI/Pages/runtime UNVERIFIED until exact run inspected. No new backend functionality or live payments.
- Next: verify exact latest HEAD workflow and browser staff/QR behaviour, then verified staff/device provisioning and TLS design. Rollback: 42fe693734a9961f4d826a6b33be200ed556083d.

# BintyPOS status

## Current-HEAD release evidence — 2026-11-05 01:03 UTC
- Canonical main at inspection: `3c3efac78851226841a324cb1fc1c981a4b9d5f4`. GitHub Actions **push** run [41825012326](https://github.com/Kenway-Creative/BintyPOS/actions/runs/41825012326), job `126557400193`, has completed **success** against this exact SHA. All 13 job steps succeeded, including Node regression tests, Python tests, Pages configuration, site upload and Pages deployment. This resolves the prior false 'no push-run evidence' blocker for that SHA.
- **That inspected SHA: COMMITTED, CI PASSED, DEPLOYED. Browser runtime: UNVERIFIED.** Public Pages URL could not be accessed by independent browser checker. No claim of production readiness or payment integration. Test counts were not available from job-step metadata (do not infer counts).
- This documentation-only update creates a later HEAD; its CI and Pages results must be verified separately before assigning those labels to the new SHA. Previous green run cannot certify this documentation commit.
- Next: independently exercise published staff and QR pages; then implement a bounded, tested secure staff/device provisioning design (no public login or live payments). Rollback known green baseline: `3c3efac78851226841a324cb1fc1c981a4b9d5f4`.


## Verified v0.2.27 workflow checkpoint — 2026-11-04 10:56 UTC
- Source commit `7236f546f1e8816b4d6626fb37e0bc271c471232`; GitHub Actions push run `41679810934`, job `126070209359`: Node regression step SUCCESS; Python regression step SUCCESS; Configure Pages, Upload site and Deploy Pages all SUCCESS (13/13 job steps). https://github.com/Kenway-Creative/BintyPOS/actions/runs/41679810934
- **Source commit: COMMITTED, CI PASSED, DEPLOYED. Runtime: UNVERIFIED.** No independent browser functionality check; this is not production readiness. Prior claims of post-fix CI being unknown below are historical and superseded by this checkpoint.
- This documentation checkpoint is a **new commit**, and its own CI/Pages evidence must be checked independently before calling the new HEAD deployed. No feature or version bump in this evidence-only update.
- Next: inspect the deployed browser artefact and verify staff/QR navigation; then plan trusted staff/device provisioning and TLS before writable HTTP. Dojo remains preferred, sandbox validation pending; no live payments.
- Rollback/source baseline: `7236f546f1e8816b4d6626fb37e0bc271c471232`.


Version: **0.2.27** — CI contract assertion repair
Date: 2026-11-03
Canonical: Kenway-Creative/BintyPOS · main
Rollback baseline: `4c1fed0f9d175e56b7207dc5571e6573fd1c2832`

## 0.2.27 patch checkpoint — 2026-11-03 16:59 UTC
- Canonical main advanced with device identifier regression cases `5c3132939969ecfa205b1cd26f16804091ae50a5` and documentation through `9139616fadd4ccbe979f1b6f8f8290cb12a52d0b`. No force push.
- Failed run 41669040598: Node tests successful; Python 111/112 successful, failure in `test_device_registry.test_invalid_inputs`; Pages steps skipped. Root cause fixed in `296373c2344a589585115350a21776ecfc8aca4f`: device identifiers now reject whitespace, leaving shared staff-directory validation intact.
- Added regression tests for whitespace in venue, device and outlet IDs. Full tests NOT executed locally (GitHub clone DNS unavailable); latest post-fix CI and Pages outcome NOT independently available. Do not claim 0.2.27 deployed or browser-verified.
- Version remains **0.2.27** for patch-level CI repair; do not increment or add features until a green CI + Pages workflow is observed for current commit.
- Last confirmed successful Pages workflow: 41641340611 (v0.2.24). Rollback baseline for this patch: `1a9b4888af2e3ef9ab9980a10f17d74c656c1db1` (not green); known working deploy workflow 41641340611.
- Next: inspect latest run on `main`, fix any remaining failed test, verify Pages deploy and public browser. Then return to secure staff/device provisioning. No real payments.

## 0.2.27 deployment hotfix — 2026-11-03
- Actual GitHub Actions run 41669040598 **failed**: Node tests passed, Python ran 112 tests with 1 failure in `test_device_registry.DeviceRegistryTests.test_invalid_inputs`; upload and Pages deployment were skipped.
- Root cause: `SQLiteStaffDirectory._valid` permits internal spaces, while device identifiers must reject `bad venue`. Fix `296373c2344a589585115350a21776ecfc8aca4f` adds stricter device-only validation without changing shared staff identifier rules.
- Latest Pages release is **not** 0.2.27 until the new CI run passes and Pages deploys. Full CI and live browser verification remain pending after hotfix.
- Last independently inspected successful workflow: 41641340611 (0.2.24), including Pages deployment.
- Next: confirm new Python and Node CI pass; do not resume feature releases until clean deployment.

## 0.2.27 checkpoint
- Identified concrete failing GitHub Actions run 41660300070: 146/148 Node tests passed; two stale v0.2.24 OpenAPI assertions failed against v0.2.26. Updated both tests to assert v0.2.27 while preserving functional contract checks. Python tests did not run because the Node gate failed. Await fresh CI; no local suite executed in this connector-only run.
- Rollback baseline: `eec0f503ad1fd131efc1c21bb5e5e7462619da9f`. Next: confirm Node and Python CI green; then secure staff/device provisioning and TLS threat model before browser or writable endpoints. No real payments.

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
