# Changelog

## [0.2.12] — 2026-11-03 — Scoped demo checkout capabilities
- Added `src/checkout_identity.py`: SQLite-persisted, random bearer capabilities stored only as SHA-256 digests; short expiry, durable revocation, venue/channel binding and internal server-derived checkout sessions.
- Checkout-facing facade allows server-priced quote, acceptance, order creation and status; staff-only mock cancellation. It deliberately excludes payment authorisation, completion and direct inventory commit.
- Added 13 Python regression tests for malformed/forged credentials, venue and session isolation, QR restrictions, expiry, revocation, restart and a mock-only checkout.
- Updated proposed OpenAPI checkoutAuth semantics, README, architecture, roadmap and status. This is not staff login, OAuth, an HTTP server, a real payment flow or production-secure authentication.
- Square benchmark: scoped/short-lived/revocable OAuth credentials and least-privilege guidance (https://developer.squareup.com/docs/auth). BintyPOS is only a local capability proof-of-concept.
- Rollback baseline: `4c1fed0f9d175e56b7207dc5571e6573fd1c2832`. No release tag unless independently verified.


## [0.2.11] — 2026-11-02 — Durable mock order lifecycle and CI contract repair
- Added SQLite-only `src/order_lifecycle.py`: accepted-quote stock hold → awaiting mock payment → mock authorisation → simulated confirmation, plus decline, cancellation, expiry and reconciliation states.
- Confirmed simulated orders atomically persist inventory movements and order state, with idempotent replay; no real payment provider is accepted.
- Added 12 Python lifecycle regression tests for replay, restart, scope fixture, expiration, failure, stock conflict, void uncertainty and no premature completion. GitHub Actions run 41549477925 **passed**: 147/147 Node tests and 39/39 Python tests; Pages deployment step succeeded (public browser not independently verified). https://github.com/Kenway-Creative/BintyPOS/actions/runs/41549477925
- Fixed stale `tests/api-contract.test.cjs` hardcoded 0.2.8 version assertion, which caused the 0.2.10 GitHub Actions run 41541876510 to fail (145/146 Node tests passed); now tests current 0.2.11 contract version.
- API documents proposed order lifecycle read and mock-only state boundaries, **not running endpoints**. Browser demo unchanged. No real payments, authenticated identities, HTTP service or Dojo integration.
- Square Orders/Payments API separates payment authorisation and order completion; BintyPOS follows state separation for local simulation, not Square-equivalent settlement or real capture. https://developer.squareup.com/docs/orders-api/pay-for-orders
- Rollback baseline: `3394a2f0ad6650fa201406efd1e73faa7eee6601`. No tag unless explicitly verified.


## [0.2.10] — 2026-11-02 — Trusted quote-bound durable stock holds
- Added `src/trusted_checkout.py` with versioned published-product fixtures, immutable GBP-pence quote snapshots, aggregated recipe demand and explicit acceptance.
- Durable holds are derived exclusively from stored accepted quotes inside a single SQLite `BEGIN IMMEDIATE` transaction. Rejected stale price/recipe revisions, expired quotes, wrong checkout session fixture and reused idempotency keys.
- Added 14 Python regression tests including competing independent connections, restart persistence, invalid client-supplied prices, no partial holds and replay safety.
- Local verification: 14/14 new Python tests passed on Python 3.13.5; source and test Git blob hashes match committed GitHub content. Native Node CI, all Python tests in GitHub Actions, and Pages outcome pending confirmation.
- OpenAPI contract updated to 0.2.10 but is **not** implemented as an HTTP API. Checkout session strings and product publishing are trusted fixtures, not authenticated endpoints.
- No payment processing, VAT/tax engine, durable order ledger, real server auth or connection to static till/QR. Do not expose direct-demand reservation methods to browsers.
- Square Inventory API benchmark: atomic batches, idempotency and event-based stock accounting. BintyPOS differs by deriving ingredient demand from accepted multi-vendor quotes, but is not operationally equivalent.
- Rollback baseline: v0.2.9 checkpoint `11f7def96b633c7573b06dde306de00373355a84`. Implementation `f3afc3163bf53f2fe62620d4fa77c7b834a9753d`, tests `5144b8d4e9d153ed003cad956da2eac3564e2f01`. No release tag.


## [0.2.9] — 2026-11-02 — SQLite transactional reservation proof-of-concept
- Added `src/persistent_reservations.py`: SQLite file-backed, transactionally serialised stock holds, expiry, release, durable idempotency and one-time ingredient movements.
- Added 13 Python standard-library regression tests, including two competing connections, restart/replay, venue isolation and no partial deduction.
- Added Python 3.13 CI gate before GitHub Pages publication. Existing 146 Node tests remain unchanged.
- Updated OpenAPI contract to 0.2.9 while explicitly keeping HTTP endpoints unimplemented.
- Local verification: 13/13 Python tests passed with Python 3.13.5; GitHub Actions result pending independent inspection.
- **No browser integration:** the static till/QR demo still uses in-memory reservations. This service is not authenticated, has no trusted quote binding or payment integration.
- Rollback baseline: v0.2.8 checkpoint `2f861e4625930da917b6f111962a89c8b892810d`. Source implementation commit: `7375f8fb51e4398b021460083fce1ce46002021b`.


## [0.2.8] — 2026-11-02
**Feature:** In-memory stock reservation boundary.
- Added `src/reservations.js` with idempotent holds/commit/release, TTL expiry, conflict checks and stock adapters.
- Staff and QR simulated checkout now reserve then commit shared ingredient stock; active holds reduce availability.
- Added 16 native Node tests, 3 UI smoke tests, 1 static wiring test and 1 API contract test. Native Node 22 GitHub Actions passed **146/146** regression tests and Pages deployment step succeeded for commit `9770d6d87cd2dde63856133972a5e28e92c2d28c` (run 41526203697); public live-browser behaviour not independently inspected.
- OpenAPI v0.2.8 specifies quote-derived reservation, status/release and trusted service-only commit. No running API or payment integration.
- Benchmark: Square atomic inventory batches and idempotency; this demo is not a distributed transaction.
- Rollback: `30aa731662bc9ba97ec7611762700e5077b5801c` (v0.2.7). No release tag.


## [0.2.7] — 2026-11-02
**Feature:** Virtual stockrooms (logical categories) with physical count breakdowns.
- Implemented `src/stockrooms.js`: ingredient belongs to exactly one virtual room, with independent counts at multiple physical locations; venue totals aggregate each ingredient once. Category reassignment retains counts and item identity.
- Stock tab now groups by virtual room and displays per-location count adjustment controls. Simulated checkout deducts the basket's aggregate recipe demand from physical counts deterministically, keeping the virtual total in sync.
- Added 12 stockroom unit tests, three UI smoke scenarios, one static wiring check and one proposed API contract test. Updated previous UI tests to change counts through the stockroom model.
- **125/125 committed tests passed in a V8 Node-compatibility harness**; application JavaScript parsed. Native Node CI, real browser/hardware and Pages deployment **not independently verified**.
- OpenAPI v0.2.7 specifies virtual-room listing, physical count submission and category reassignment. **These are contracts only, not running endpoints.**
- Benchmark: Square Inventory API physical counts and location-aware adjustments; BintyPOS models an additional venue-wide logical counting category. https://developer.squareup.com/docs/inventory-api/how-it-works
- Rollback baseline: `a6f46b32345fd874a56442d8e2c9676b8f9c3f8c` (v0.2.6). No tag or release created.


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
