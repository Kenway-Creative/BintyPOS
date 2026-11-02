# Changelog

## [0.2.6] — 2026-11-02
**Feature:** Combined recipe ingredient preflight for the whole staff/QR basket.
- Added pure `src/inventory.js` to aggregate demand across different products and vendors; missing stock is zero, invalid counts/recipes are rejected and shortages are returned with required/available quantities.
- Staff till and QR additions now consider ingredients already allocated to the current basket. Checkout revalidates the entire basket against current stock and uses a new stock snapshot only on success, with no partial deductions or negative stock.
- Added 10 Node unit tests, three UI smoke tests, one static wiring test and one API contract test. **108/108 committed regression cases passed in a V8 Node-test compatibility harness**. The 10 standalone inventory tests also passed under native Node 22 in an isolated local copy. Inline application JavaScript parsed and four inventory-specific UI scenarios plus one aggregate module check passed in V8.
- OpenAPI v0.2.6 specifies an advisory inventory preflight endpoint and shortage schema. **No running API, server-side reservations or live Dojo payments.**
- Square Inventory API uses atomic batches and stock adjustment history; its documentation notes ingredient/subcomponent tracking limitations. This prototype's shared-ingredient basket guard is not a transactional inventory ledger. References: https://developer.squareup.com/docs/inventory-api/how-it-works and https://developer.squareup.com/docs/inventory-api/what-it-does .
- Native GitHub Actions status, GitHub Pages deployment, real browser/device and concurrent multi-till behaviour **not independently verified**.
- Rollback baseline: `0c37d28cba14fbf9db24cd4d516abeb3d50389c8` (v0.2.5). No tag or release created.

## [0.2.5] — 2026-11-02
**Feature:** Immutable basket price snapshots with explicit review before simulated checkout.
- Added `src/basket.js`: defensive line snapshots containing product/version, vendor, name, unit price in GBP pence and quantity; minor-unit totals; changed/unavailable/deleted catalogue conflict detection; explicit repricing; validated order snapshot.
- Staff till and guest QR share the same locked basket. Approving a new outlet price no longer silently recalculates an in-progress basket; checkout blocks until staff/guest explicitly accepts current published prices. Unavailable products must be removed.
- Simulated orders retain accepted price/vendor snapshots for historical reporting. Existing stock checks and voucher demonstration remain browser-only.
- Proposed server-authoritative quote, quote acceptance and quote-referenced order contracts in `openapi.yaml`; **no API server or Dojo connection**.
- Added 12 basket unit tests, four UI smoke tests, one static wiring test and three API contract checks. **93/93 committed tests passed in a V8 compatibility harness**. Inline app syntax and five direct mocked-DOM flows passed. Native Node CI, real browsers and Pages publication **not independently verified**.
- Benchmark: Square's order line items record base price money per unit (https://developer.squareup.com/reference/square/objects/orderlineitem); Toast recommends validating/pricing before order submission (https://doc.toasttab.com/doc/devguide/apiOrdersFirstOrder.html). BintyPOS adds explicit acceptance of changed published prices, but has no real server-side pricing or tax engine.
- Rollback baseline: `2f0ec0182ce49d6f83e88775d47fa26df6c4b656` (v0.2.4 checkpoint). No tag or release created.

## [0.2.4] — 2026-11-02
**Feature:** Outlet-managed offering proposals with venue-controlled publication.
- Added `src/offerings.js`: versioned published product snapshots, outlet-scoped draft proposals, central approve/reject, stale-version protection, defensive snapshots and an append-only in-memory event sequence.
- Back office now stages name, availability and price changes without affecting staff or QR until a venue admin approves. Venue review queue lists pending proposals and supports approval/rejection. Removed immediate price mutation.
- Shared staff/QR catalogue updates only after approval. Demo checkout blocks items whose published availability changed to unavailable.
- Added 15 module tests, 4 UI smoke tests and 1 static wiring test; **73/73 tests passed in a V8 compatibility harness**. Native Node CI, real browser/device checks and live Pages deployment are not independently confirmed.
- Proposed REST v1 offering proposal and approval endpoints in `openapi.yaml`; **no running API server**. API uses integer GBP pence while browser demo uses pound-number prices.
- Benchmark: Toast menu edit/publish permissions (https://doc.toasttab.com/doc/platformguide/platformMenuManagerPermissions.html), reviewed 2026-11-02. BintyPOS demo requires explicit venue approval of every outlet proposal.
- Limitations: public demo PINs, no server-enforced roles, browser-only audit, no durable state. Publishing a new price can reprice an existing basket; price snapshots are next.
- Rollback baseline: `19315ca624cefd6bffcb75370e132617179fbdbd` (v0.2.3 checkpoint). No tag/release created.


## [0.2.3] — 2026-11-02
**Feature:** One-tap staff speed keys and category jumps, independently configurable per selling area.
- Added pure `src/shortcuts.js` with ordered per-area favourite product IDs (max eight) and category jumps (max six), validated against known products/categories.
- Added unpublished drafts, explicit publish/discard, version conflict checks, history snapshots and defensive copies. No draft affects staff till until published.
- Staff till displays published favourites as direct-add buttons and category jumps; a category jump resets the outlet folder but keeps the shared basket. Guest QR has no staff shortcuts.
- Published shortcut projection intersects with the published area keyboard; a restricted outlet cannot expose a favourite owned by an excluded vendor. Existing stock checks still apply.
- Added 14 pure module tests, 3 demo wiring tests and 8 Node VM UI smoke tests. **53/53 tests passed in a V8 Node-test compatibility harness**, including the eight VM smoke scenarios through a compatibility shim; 10 additional mocked-DOM interaction assertions passed. Native Node CI execution has not been independently verified.
- Added proposed versioned shortcut GET/draft/publish API contracts in `openapi.yaml`; no running API.
- Benchmark: Toast Retail recommends a speed screen or manageable category for fast access to non-scannable products (https://support.toasttab.com/en/article/Toast-for-Restaurant-Retail-Ordering-of-POS-Buttons). BintyPOS adds independently published, area-specific shortcuts filtered through multi-vendor keyboard visibility.
- Implementation commits: `461d2456eaf2574b3dbbc696db78258c8cb8b885` (module), `c6712e62cd132c5313dca109680a46720cb28d33` (UI), `deec17cf733817331cf1c4694eb0a2bc7a70a35f` (demo tests), `285366d8726a144dd8e6af9cc3935a1684b22b04` (VM smoke tests), `f0c8bfac851a808aa92797dc7fab9979e86150ed` (API).
- Rollback baseline: `178b3a9257a50d31afb046f88bb47083185bc82d` (v0.2.2). No tag/release or live Pages success claimed.


## [0.2.2] — 2026-11-02
**Feature:** Versioned selling-area keyboards with staged drafts and explicit publishing.
- Added pure `src/keyboards.js` store: all/short/selected-outlet profiles, defensive copies, draft/discard/publish, optimistic version checks, validation and history snapshots.
- Venue-admin demo can select multiple outlets for a bar till, review unpublished changes and publish a new version. Till and guest QR continue reading the published version until publication; shared basket survives profile changes.
- Added 11 keyboard tests and 2 new demo checks; adapted existing script-order test. 28 committed test functions passed in a V8 Node-test compatibility shim, plus 10 mocked-DOM smoke checks. **Not verified with native Node CI or a live browser.**
- Added planned keyboard draft/publish REST endpoints and auth/If-Match contracts to `openapi.yaml` (no running server).
- Market reference: Toast saved-versus-published configuration and publish permissions (https://support.toasttab.com/en/article/Global-Publishing-Experience-in-Toast-Back-End).
- Rollback baseline: `d3add5043483d7560f6ef6dde48283e41a6e96b7` (v0.2.1). No tag or release claimed.


## [0.2.1] — 2026-11-02
**Feature:** Shared catalogue projection for fast bar outlet folders and QR parity.
- Extracted pure `src/catalog.js` module for sales-area policy, outlet shortcuts, category tabs, search and channel-aware filtering.
- Staff tills show only outlets allowed by the selected area; guest QR ignores staff navigation folders but respects the area restriction.
- Area changes reset folder/search filters while preserving the multi-vendor basket.
- Added 12 Node catalogue tests and 3 static-demo checks; GitHub Pages workflow now runs tests before deployment.
- Verification performed: 12 V8 module assertions, inline script parse and 5 simulated-DOM interaction checks. **Node GitHub Actions run and browser deployment not yet confirmed.**
- Implementation commits: `785fa59`, `2a27a72`, `f22bf98`, `760136c`, `3d01cac`.
- Rollback baseline: `dbdb298f9e833777d9fe39a6194dcb3432572c9a` (before feature). Do not force-push; revert offending commits or redeploy a verified checkpoint.

## [0.2.0] — 2026-11-02
- Architecture specification, proposed OpenAPI contract, roadmap, status and release process. API not yet implemented.

## [0.1.2] — prior
- Outlet shortcuts, manager demo PINs and back-office controls in browser-only simulation.

## Release policy
Keep every verified version in Git history. Tags/releases are not claimed until created and confirmed. Record exact commit hashes and limitations; never label a prototype as production-ready.
