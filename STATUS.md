# BintyPOS status

Version: **0.2.6** — combined recipe ingredient preflight
Date: 2026-11-02
Canonical: Kenway-Creative/BintyPOS · main
Rollback baseline (v0.2.5): `0c37d28cba14fbf9db24cd4d516abeb3d50389c8`

## Completed this release
- Pure `src/inventory.js` validates integer stock/recipe counts, aggregates demands across the full multi-vendor basket, reports shortages and returns all-or-none stock snapshots.
- Staff till and guest QR now use the same basket-wide stock guard. The remaining count for an item considers ingredient demand already in the basket, including other product recipes.
- Simulated checkout validates the accepted price snapshot and current inventory together. If one ingredient is short, no order is recorded and no stock is decremented. If all fit, one new stock snapshot replaces the old one.
- Proposed advisory inventory preflight API and shortage schema added to OpenAPI v0.2.6. No running endpoint.

## Verification performed
- **108/108 committed regression cases passed in a V8 Node-test compatibility harness** across nine test files (including ten new inventory tests, three UI smoke scenarios, one static wiring check and one API contract check).
- **10/10 inventory unit tests passed in native Node 22** using an isolated local copy of the inventory module/test; not a full native repository CI run.
- Inline application JavaScript parsed in V8. Five additional direct V8 checks passed: syntax, aggregate demand, oversell add guard, stock-reduction checkout block and successful checkout.
- Native GitHub Actions, real browser/device, GitHub Pages deployment and multi-client concurrency **not independently verified**.

## Implementation commits
- Inventory module: `1ebf4cdae0022f04ed7763cfada2e9c60b90ea5b`
- Unit tests: `5575b4e922481b7574a3e6b813914195229329b2`
- Staff/QR wiring: `8c7e69d956da8effbffb52ff007c4f6c44b9e1d3`
- Static and UI tests: `6878a3eb365c7a51baef0e4e0a059355eedf2166`, `f880818bed252878341c8f45f5bf45f9d012a18c`
- API contract and test: `7a0c8b516b7c125e029f9bdd323e39d95332d292`, `2ce9bddb36cadf5383598ee23cc6ca53cb490969`

## Known limitations
- Client PINs, inventory, prices, orders and audit remain browser-controlled and ephemeral. No secure login, persistent server, transactional reservation or Dojo integration.
- Integer stock units are only suitable for this demo. Production requires units of measure, yield/waste, recipe versions, per-location pools, physical counts and stock movement history.
- This local all-or-none update is not concurrency safe across devices. Real checkout must reserve ingredients atomically and coordinate idempotent payment confirmation/refunds. Do not treat advisory preflight as a stock guarantee.
- GitHub Pages and native GitHub Actions outcomes remain unconfirmed.

## Next bounded feature
**0.2.7 — Inventory reservation contract and adapter boundary**: explicit stock pool, recipe revision, reservation expiry and idempotency states; test transitions and failures without pretending the demo has a transactional backend.

## Market comparison
Square's Inventory API documents batched atomic adjustments and physical-count reconciliation, while noting that its standard Inventory API does not directly track ingredients/subcomponents. BintyPOS v0.2.6 aggregates ingredients across independently owned vendors in a single venue basket, but remains a browser simulation.
- https://developer.squareup.com/docs/inventory-api/how-it-works
- https://developer.squareup.com/docs/inventory-api/what-it-does
