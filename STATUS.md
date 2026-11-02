# BintyPOS status

Version: **0.2.7** — virtual stockrooms and physical count locations
Date: 2026-11-02
Canonical: Kenway-Creative/BintyPOS · main
Rollback baseline (v0.2.6): `a6f46b32345fd874a56442d8e2c9676b8f9c3f8c`

## Completed this release
- `src/stockrooms.js`: one logical category per ingredient, separate per-location physical quantities, venue-wide totals, reclassification without losing counts, deterministic local consumption and no partial depletion on shortage.
- The Stock tab groups by virtual room, shows physical location counts and permits illustrative +/- changes.
- Staff and QR checkout still preflight the full basket using shared recipe demand, then decrement physical locations in the same browser state. The selling area does not determine which stock pool is depleted.
- OpenAPI v0.2.7 adds proposed logical room listing, physical count and category-reassignment routes. These are **not operational endpoints**.

## Verification
- **125/125 committed test cases passed in a V8 Node-compatibility harness** across 10 test files; inline application JavaScript parsed.
- 12 stockroom unit tests, 3 new UI smoke scenarios, 1 static wiring check and 1 new API contract check included in total.
- Native Node GitHub Actions, live Pages deployment, real browser/hardware and concurrent multi-device stock operations **not independently verified**.
- Stockroom module commit: `f2f72f65d9eccadb3d8b703a0d9d7d09f1f818df`; validation fix `27c926b68142a2cd90d905453ed9140a7443559d`.
- Demo wiring: `095bfa78b6eb961208a2ce5bfc8d17010dfe832d`.
- Regression test correction: `c46aca2d5291222fa733196dc875e691edac6af9`.
- OpenAPI contract: `e6b3e85e3ee6f26616451329a6fe83aad781a3ec`.

## Limitations
- All counts, PINs, orders and audit are browser memory only. Physical count controls have no secure permissions or stocktake approval. Quantities are illustrative integer units.
- Physical location depletion is alphabetical and **not** a fulfilment/picking rule. The stockroom model does not reserve stock or reconcile real-world variances.
- A real system requires server-authenticated staff, durable stock movements, UOM/yield/waste, stocktake sessions, revision checks, transactional reservations, idempotency and Dojo sandbox integration before trading.

## Next bounded feature
**0.2.8 — inventory reservation boundary:** isolate a server-style atomic reservation interface with idempotency keys, expiry and conflict tests, while clearly separating a pure simulator from real database transactions.

## Market comparison
Square's location-aware physical count and adjustment model informs this feature; BintyPOS adds a logical venue-wide counting category separate from physical locations to match Binty's explicit scoping requirements. https://developer.squareup.com/docs/inventory-api/how-it-works
