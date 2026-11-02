# BintyPOS status

Version: **0.2.5** — immutable basket line prices and explicit catalogue-change review
Date: 2026-11-02
Canonical: Kenway-Creative/BintyPOS · main
Rollback baseline (v0.2.4): `2f0ec0182ce49d6f83e88775d47fa26df6c4b656`

## Completed this release
- `src/basket.js` stores per-line product ID, published version, outlet ownership, name, quantity and GBP-pence price snapshots. Adding further quantity retains the original price until deliberate acceptance.
- `review()` detects changed, unavailable or removed products; `validatedOrder()` blocks checkout on any conflict; `acceptPublished()` explicitly updates a still-available line to the current published version and price.
- Staff and QR now display locked basket prices. Venue-approved price changes produce a visible review warning instead of silently repricing. Simulated order lines preserve accepted snapshots for reporting.
- Proposed quote issuance, explicit price acceptance and quote-referenced order submission documented in `openapi.yaml`. These are not running API endpoints.

## Verification performed
- **93/93 committed regression cases passed** in a V8 Node-test compatibility harness (eight test files, including 12 new basket tests, four UI basket smoke cases, one static wiring case and three API contract cases).
- Inline application JavaScript syntax parsed successfully in V8.
- Five additional mocked-DOM scenarios passed: add item, approve new price, preserve original basket price and display warning, block stale checkout, explicitly accept and complete simulated checkout.
- Native Node CLI/CI, browser/device tests, and GitHub Pages deployment **not independently verified**. Do not infer deployment success from these tests.
- Tests are reproducible with Node 20+ using `node --test tests/*.test.cjs` from repository root.

## Source commits
- Basket module: `6c6fa2e3fe2afe2614605b3ac1a0548d47e6b598`
- Basket unit tests: `d4fa2b82fba6a7bf2ecbb5a68a82dd6b934f9e94`
- UI wiring: `ceb94b0330169608331eb0d84b1e22ea8f2d4eda`
- UI review: `38ecf38660a58c0977da7faf1a64752aba3012f5`
- Test wiring and UI smoke: `0cad1004eefd50e1b519092d1c2ece42bf834989`, `73314f1a9f08038c76a341b3fd2825888e033e42`
- API contract: `f5249a4448e14e0e97fa9854f3b67b78392a1682`
- API contract tests: `49b3873b4e54e09d98c4614783f07bb95b84e923`
- Changelog: `87626d3764011d33c23603a08b5abfcdb1377592`

## Known limitations
- Demo PINs, actor claims, baskets, prices, stock and audit records remain browser-controlled and ephemeral. **No secure authentication, persistent API or real payments**.
- Snapshot/review is a UX safeguard, not an enforceable quote. A real server must reprice and validate, apply VAT/discounts, atomically reserve inventory and coordinate Dojo payment state idempotently.
- The UI still uses GBP pound-number calculations for voucher demonstration; basket line prices and subtotal are integer pence. Vendor settlements and tax are not implemented.
- GitHub Pages publication and native GitHub Actions outcome remain unconfirmed.

## Next bounded feature
**0.2.6 — Pure recipe inventory preflight** for a combined multi-vendor basket: calculate ingredient demand, detect insufficient shared stock and refuse negative-stock checkout, with tests. This is only a local prototype; transactional reservations require a backend.

## Market comparison
Square Orders API uses `base_price_money` on line items; Toast recommends pricing/validating before submission. BintyPOS adds an explicit stale-price acceptance step for a shared multi-outlet basket, but does not yet provide a trusted server order engine.
- https://developer.squareup.com/reference/square/objects/orderlineitem
- https://doc.toasttab.com/doc/devguide/apiOrdersFirstOrder.html
