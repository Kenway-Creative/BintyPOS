# BintyPOS status

Version: **0.2.9** — standalone SQLite transactional reservation proof-of-concept
Date: 2026-11-02
Canonical: Kenway-Creative/BintyPOS · main
Rollback baseline (v0.2.8): `2f861e4625930da917b6f111962a89c8b892810d`
Implementation commit: `7375f8fb51e4398b021460083fce1ce46002021b`

## Implemented
- `src/persistent_reservations.py` is a standalone Python standard-library SQLite adapter. `BEGIN IMMEDIATE` serialises competing writers to one file. Holds, expiry, release, per-venue idempotency, stock consumption and ingredient movements are durable and atomic.
- `tests/test_persistent_reservations.py` covers competing independent connections, reopen/restart, duplicate commit, shortages, expiry, release, isolation and failure safety.
- CI workflow now runs Python 3.13 unittest discovery **as well as** the existing Node regression suite before Pages deployment.
- OpenAPI 0.2.9 explicitly labels the HTTP routes proposed only; the SQLite adapter is not an API server.

## Verification
- **13/13 Python tests passed** locally under Python 3.13.5 on 2026-11-02; Python bytecode compilation passed.
- Git blob hashes of locally tested files exactly match the committed GitHub blobs: source `88d876f8386254c12b55a3b35edd233d53775bb6`, tests `9088ca7f783c384df701bc983dcb82efddb3bdcd`.
- Existing v0.2.8 Node suite last verified **146/146** in GitHub Actions run 41526203697; unchanged in this release.
- **New GitHub Actions run and Pages deployment not independently confirmed** for v0.2.9. No live browser/hardware tests.

## Limitations
- Existing browser demo still uses `src/reservations.js` and cannot share holds between tills; SQLite proof-of-concept is not wired to the UI.
- Direct-demand Python adapter has no authenticated actor, accepted server quote, authoritative recipe binding, HTTP listener, order/payment state machine, Dojo connection, migrations/backups, or multi-host DB support. Never expose directly to browsers.
- Demo PINs remain insecure. No real card payments or Spektrix integration.

## Next bounded feature
**0.2.10 — bind durable reservations to trusted, accepted, server-priced quote snapshots**, with recipe-version and idempotency checks. Prove server-side trust boundaries in tests before any public HTTP API.

## Market comparison
Square Inventory API supports atomic batched stock adjustments and idempotency keys. BintyPOS now proves local transactional multi-ingredient holds; it is not production-equivalent to Square's inventory service.
https://developer.squareup.com/docs/inventory-api/how-it-works
https://developer.squareup.com/reference/square/inventory-api/BatchChangeInventory
