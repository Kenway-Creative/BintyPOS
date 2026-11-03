# BintyPOS — Blackstock Market EPOS prototype

**Prototype v0.2.12** · public demonstration only · no live payments or merchant data.

BintyPOS is a modular, API-first concept for one venue containing many independently managed businesses. The goal is a fast bar till, flexible outlet keyboards, a shared basket and catalogue for staff and QR, reliable inventory, and auditable vendor reporting. It is **not** ready for trading.

## Scoped demo checkout identity (v0.2.12)

The standalone SQLite facade `src/checkout_identity.py` provides **server-generated, short-lived, venue-scoped bearer capabilities** for simulated staff and QR checkout. Tokens are random, persisted only as SHA-256 digests, revocable, and mapped to an internal session ID. All quote, accept, create-order and order-status calls derive their session from the capability; a QR capability cannot call the staff-only mock cancellation operation. The facade does **not** expose authorise/confirm/stock-commit operations to checkout callers. Those remain trusted-internal simulation methods.

Example **trusted fixture only**: `api = ScopedDemoCheckout(db_path)` → `api._orders.bootstrap_stock(...)` / `api._orders.publish_product(...)` → `identity = api.bootstrap_demo_identity("blackstock","staff")` → `api.create_quote("blackstock", identity["token"], [{"productId":"beer","quantity":1}])` → `api.accept_quote(...)` → `api.create_order(...)` → `api.status_order(...)`. The `bootstrap_demo_identity` and `revoke_demo_identity` methods are **trusted test/bootstrap hooks, not login endpoints**; never expose them publicly. The `_orders` attribute gives trusted Python callers access to the underlying mock service and must never be returned to clients.

**Security limitations:** This is not verified human/staff authentication, hardware pairing or a production session service. Whoever possesses a demo bearer capability can use it. No TLS, login/MFA, token refresh, rate limits, audit log, staff role/outlet mapping, or running HTTP API exists. Capability validation and subsequent order mutation use separate SQLite transactions, so revocation can race an in-flight call; an operational implementation must enforce auth and mutation atomically. The existing `SQLiteMockOrders` and `SQLiteReservations.commit` methods remain callable by trusted Python code only and must never be exposed to a browser. Browser PINs are unchanged and insecure; no Dojo or real payments.

Run `python3 -m unittest discover -s tests -p 'test_*.py' -v`. The new `tests/test_checkout_identity.py` covers token hashing, venue/session isolation, expiry, revocation, restart persistence, channel permissions and a mock-only order flow. OpenAPI v0.2.12 describes proposed bearer-authenticated checkout routes, **not running endpoints**.

## SQLite mock order lifecycle (v0.2.11)

The isolated Python module `src/order_lifecycle.py` extends trusted quote-bound stock holds with a durable **simulation-only** order state machine: `awaiting_payment → authorised → confirmed`, plus `failed`, `released`, `expired` and `needs_reconciliation`. The only accepted payment implementation is `MockPaymentAdapter`, which performs **no network I/O, card authorisation, capture or money movement**. A simulated completion and ingredient movement are committed in one SQLite transaction, with idempotent confirmed-order replay. Mock declines and cancellations release holds; ambiguous simulated capture/void and stock conflicts fail closed for reconciliation. Session strings are **not authenticated identities**.

Example internal fixture: `SQLiteMockOrders(db)` → `bootstrap_stock` / `publish_product` → `create_quote` → `accept_quote` → `create_order(venue,session,quoteId,key)` → `authorise_mock(venue,session,orderId)` → `complete_mock(...)`. Run `python -m unittest discover -s tests -p 'test_*.py' -v`. **No HTTP endpoint or live till/QR connection exists.** Direct inherited `commit` remains an internal, payment-unchecked method and MUST NOT be exposed. Crash between hold and order insertion can leave a time-limited orphan hold. Before any real payment integration: implement verified identities, server permissions, a transactional order/outbox and reconciliation, tax/VAT, payment adapter contracts, Dojo sandbox validation and cross-device tests.

## Run the demo
Open `index.html` using a local HTTP server (for example `python3 -m http.server 8000`) and visit `http://localhost:8000/`. GitHub Pages deploys through the GitHub Actions workflow in `.github/workflows/deploy.yml`, not branch-source publishing. The GitHub Actions Pages deployment step succeeded for v0.2.11 (run 41549477925); the public site has not been independently inspected in a browser.

Try: Main Bar → Pattersons folder → add Burger → Spuddy Hell folder → add Loaded Spud → one simulated checkout. Switching folders keeps the shared basket. Change the sales area to Pattersons and notice only that area's products and shortcuts appear. Guest QR reads the same catalogue but ignores staff-only folder selection. Back-office demo PINs are printed on screen and are **not secure**. On the staff till, try the **Speed keys** (Corona, Burger and Loaded Spud) for one-tap additions, or **Jump to category** (Food, Packaged, Cocktails) to navigate in one tap without losing the basket. Shortcuts are specific to the selected area and never appear on guest QR. As venue admin (demo PIN 2468), open **Back office → Published till keyboard**, choose Main Bar, select **Selected outlets**, toggle the desired vendors, and **Publish keyboard**. Draft changes remain invisible to staff and QR until publishing; the live version increments. Discard reverses an unpublished draft. In **Back office → Speed keys and category jumps**, select an area, stage up to eight favourite products and six category jumps, then publish; the till retains the old version until publication. Reload resets all profiles.

## Outlet offerings and central approval (v0.2.4)
Use **Back office** with an outlet demo PIN (Pattersons 1357, Spuddy Hell 8642, Cherry On Top 9753). Select one of that outlet's products, change its name, availability or price, then choose **Submit for approval**. The staff till and guest QR remain unchanged while the proposal is pending. Log out and enter venue admin demo PIN 2468 to view the **Venue approval queue**; approve and publish or reject the proposal. A successful publish increments the product version and updates the shared staff/QR catalogue. Rejection leaves the published catalogue unchanged.

All role checks, proposal history and approvals here run in **browser memory only**; client-side PINs and actor claims are insecure. Real API calls must derive identity and outlet scope server-side, require central approval, store audit events durably and reject stale revisions. **Prototype limitation:** basket snapshots and checkout revalidation are browser-only; real checkout must use server-issued quotes and atomic stock reservation.

## Basket price snapshots and review (v0.2.5)
When staff or a guest adds a product, BintyPOS captures the published product version, vendor, name and unit price in **integer GBP pence**. Existing basket totals are not silently recalculated when an outlet's price is approved. The basket shows a review warning when a product version, price, availability or ownership changes. A price/version conflict blocks simulated checkout until the operator deliberately clicks **Accept published prices**; an unavailable or removed product must be removed from the basket. The simulated order retains the accepted line-price snapshot for reporting.

To test: add Pattersons Burger (£12.50), use the Pattersons demo manager to propose £14.00, then approve with venue admin. Return to the till: the basket still shows £12.50, checkout is blocked, and accepting the revised price changes the basket to £14.00. All behaviour is local demo state and is **not a real price guarantee**.

`src/basket.js` is a pure CommonJS/browser module with immutable line snapshots, minor-unit totals, catalogue conflict detection, explicit repricing, and validated order snapshots. `tests/basket.test.cjs` contains 12 unit tests; the UI smoke tests include four basket scenarios. `tests/api-contract.test.cjs` checks the proposed quote API.

**Server boundary:** Real price quotes must be calculated from the authoritative catalogue, with server-side identity, availability, VAT, promotions, atomic inventory reservation and expiry. The proposed `/api/v1/venues/{venueId}/quotes` and explicit accept-prices endpoints are **specification only**. Dojo remains the preferred future payment provider, not connected.

## Combined recipe stock preflight (v0.2.6)

Staff and guest QR now check **aggregate ingredient demand across the whole basket**, not just the quantity of each product separately. Example: four individual Coronas plus a five-Corona bucket require nine bottles; if stock is eight, the second addition is refused. If stock is reduced after items were added, checkout refuses the whole order without partially decrementing any ingredient.

The shared `src/inventory.js` module exposes `preflight(lines, products, stock)` (pure, returns ingredient demand and shortages) and `consume(lines, products, stock)` (returns a new stock snapshot or throws; never mutates its input). Demo stock and recipes use **integer units**; a real kitchen inventory will need measured quantities, stock locations, yield/waste and recipe versioning. Empty recipes are treated as untracked items.

**Important:** This is browser-only and does **not** reserve inventory. Multiple devices could still oversell the same stock. A production server must derive authoritative recipes and stock pools, atomically reserve all ingredients within a database transaction, use idempotent order/payment state transitions, and record durable stock movements. The proposed `POST /api/v1/venues/{venueId}/inventory/preflight` is an advisory API contract only, not a running service.

Test locally with `node --test tests/*.test.cjs` on Node 20+. Ten new native Node unit tests were run against the standalone inventory module; the full committed suite of 108 tests was exercised in a V8 Node-compatibility harness. Native GitHub Actions and real-browser deployment are not independently confirmed.

## Virtual stockrooms and physical counts (v0.2.7)

The **Stock** tab now groups ingredients by logical stockroom category (for example, *Communal spirits*) while showing independent counts for each actual place (Main Bar, Lily's Lounge, Cellar and Kitchen). A communal item such as vodka belongs to exactly one logical category but can have quantities counted at several locations. The count controls demonstrate how totals and availability respond to physical-location adjustments.

Simulated checkout uses the existing aggregate recipe preflight and then deducts ingredient demand from the physical counts in deterministic location-ID order; the virtual room total is the sum of its physical locations. Selling from any staff area or QR affects the same logical stock pool. This **does not model physical picking or routing**: a future fulfilment adapter must choose a location based on actual service area and stock allocation. This demo does not have audit-grade stocktakes, a ledger, durable counts, concurrent reservations or production units of measure.

`src/stockrooms.js` exports `createStore({rooms,locations,items})`, whose store supports `totals()`, `countSheet(roomId)`, `setCount(itemId,locationId,quantity)`, `moveRoom(itemId,roomId)`, `consume(demands)` and `snapshot()`. Reclassification preserves physical counts. All API routes in `openapi.yaml` are **proposed only**; the physical count and reclassification routes require server-side identity, permissions, revision checks and durable reconciliation when implemented. The Stock tab +/- buttons are **unsecured local demo controls**, not a real manager console.

**Verification:** 125/125 committed tests passed in a V8 Node-compatibility harness; application JS parsed. Native Node CI, real browser and live Pages status remain unverified.


## Trusted quote-bound SQLite holds (v0.2.10)

The **internal-only** `src/trusted_checkout.py` extends the standalone SQLite reservation proof-of-concept. It persists a versioned published-product fixture catalogue (vendor, GBP-pence price, availability, recipe), issues a server-priced quote from **product IDs and quantities only**, stores its immutable line/recipe snapshot, requires explicit acceptance of the quoted total, then atomically reserves the persisted recipe demand under the same SQLite writer transaction. If a product or recipe is republished before acceptance/reservation, the old quote is rejected as stale. Each quote binds to one checkout-session **fixture** and at most one idempotency key; competing connections cannot double-reserve the same ingredient stock.

**Trust boundary:** `publish_product()` is a trusted fixture/admin hook, **not** an authenticated back-office endpoint. The `session` string is a test identity, **not** a login or verified token. The inherited `SQLiteReservations.reserve(venue,key,demands)` remains a low-level trusted test method and must **never** be exposed to browsers. Real HTTP callers must never supply prices, recipes or stock demand. There is no HTTP listener, live server, persistent user authentication, VAT/tax/discount calculation, order ledger, Dojo connection or payment confirmation. The browser demo is still completely separate.

Example internal test sequence: `publish_product(venue, product, business, price_minor, recipe)` → `create_quote(venue, session, [{"productId":"beer","quantity":2}])` → `accept_quote(venue, session, quoteId, expected_total_minor)` → `reserve_accepted_quote(venue, session, quoteId, idempotency_key)`. **Do not call `commit()` for a real sale**: the inherited commit method does not verify payment. For demonstration only, commit is exercised by unit tests.

Run `python3 -m unittest discover -s tests -p 'test_*.py' -v` on Python 3.11+. Fourteen new quote-bound tests cover authoritative pricing, aggregated recipe demand, acceptance, expiry, stale versions, venue/session scope, idempotency, restart persistence and competing independent connections. Locally the 14 new tests passed under Python 3.11+; the existing 13 reservation tests and Node regression suite require the GitHub Actions gate for this commit.

**Next:** implement verified server-side checkout identity, authorised area/catalogue publishing and order/payment state transitions, then connect an authenticated HTTP API. Dojo remains preferred and must be validated in sandbox before any live payment implementation.

## SQLite transaction proof-of-concept (v0.2.9)

The isolated Python standard-library adapter `src/persistent_reservations.py` is a **real SQLite-file-backed transaction prototype**, separate from the browser demo. It has no network listener or payment connection. `SQLiteReservations(path)` opens a new database connection for each operation, uses `BEGIN IMMEDIATE` to serialise competing writers, and persists holds, expiry, release, idempotency keys, stock and immutable per-ingredient movements. It provides `bootstrap_stock(venue, counts)` **for isolated test fixtures only**, plus `reserve(venue, key, demands, ttl_ms)`, `status(venue, key)`, `release(venue, key)`, `commit(venue, key)`, `available(venue)` and `movements(venue, key)`.

Run independently with Python 3.11+ (no external packages): `python3 -m unittest discover -s tests -p 'test_*.py' -v`. The 13 new tests exercise concurrent connections to one file, restart persistence, duplicate commit protection, venue isolation, expiry, conflicting idempotency keys, no-partial-deduction and durable movement history. The existing browser demo and 146 Node regression tests are unchanged; CI now runs **both** suites before deploying Pages.

**Security and operational boundary:** This is **not** a running `/api/v1` server and must never be exposed directly to browsers. Its direct `demands` argument is suitable for trusted fixture tests only. A production service must authenticate checkout sessions, derive demands from accepted server-priced quotes and versioned recipes, bind reservations to orders, verify payment state before consumption, handle payment failure/reconciliation, maintain backups/migrations, and prove contention/load and recovery. SQLite is a local concurrency demonstrator, not a selected production multi-host database. Browser holds still use `src/reservations.js` and are **not synchronised** with SQLite. No Dojo, Spektrix or real payments.

## Shared stock reservation boundary (v0.2.8)

The staff till and guest QR simulated checkout now hold stock before consuming it. `src/reservations.js` injects `readStock()` and all-or-none `consumeStock()`, exposing `reserve({key,demands,ttlMs})`, `commit(key)`, `release(key)`, `status(key)`, `available()` and `activeCount()`.

Within **one browser**, active holds reduce reservable stock, idempotency prevents duplicate consumption, holds expire or release, and physical count changes can invalidate a hold. The default hold is two minutes; the demo commits immediately at simulated checkout, with no card authorisation.

**Not a distributed stock lock.** Two browsers can oversell. Production requires server-derived ingredient demand from accepted quotes, authenticated checkout sessions, transactional database stock reservation, durable idempotency and expiry, immutable movements, payment reconciliation and crash recovery. The proposed REST reservation endpoints are **not running**; internal commit must never be callable by a browser.

Run `node --test tests/reservations.test.cjs` (16 native Node tests) or `node --test tests/*.test.cjs` (whole suite). The full 146-test native Node 22 GitHub Actions run passed; the demo's real multi-device behaviour is still unverified.

## Source structure
- `index.html` — static touch demo, simulated transactions and illustrative products.
- `src/catalog.js` — pure, reusable catalogue projection for sales areas, outlet folders, category tabs and text search.
- `src/basket.js` — immutable per-line price snapshots, explicit review and integer-pence subtotals.
- `src/inventory.js` — pure aggregate recipe demand, shortage detection and all-or-none local consumption.
- `src/trusted_checkout.py` — internal SQLite versioned product/quote snapshots, explicit acceptance and atomic recipe-derived holds (no HTTP/auth/payment).
- `tests/test_trusted_checkout.py` — 14 trusted quote/stock contention regression cases.
- `src/reservations.js` — temporary idempotent holds, expiry, conflicts and injected commit adapter; demo-only.
- `tests/reservations.test.cjs` — 16 reservation unit tests.
- `src/stockrooms.js` — logical virtual stockroom categories, independent physical count locations, deterministic local depletion and safe reclassification.
- `tests/stockrooms.test.cjs` — 12 unit cases for virtual pools, physical locations, category moves, defensive snapshots and no-partial-consumption.
- `tests/inventory.test.cjs` — 10 unit tests for shared ingredient demand, validation and no-partial-deduction behaviour.
- `tests/basket.test.cjs` — 12 price-snapshot, validation and conflict regression tests.
- `tests/api-contract.test.cjs` — 3 proposed quote contract checks.
- `src/offerings.js` — pure staged offering proposals, outlet scope checks, venue-only publication, optimistic versions and in-memory audit events.
- `tests/offerings.test.cjs` — 15 regression cases covering scope, validation, publish/reject, audit and defensive snapshots.
- `src/shortcuts.js` — pure per-area staff speed-key store with staged/published versions, validation and visibility intersection.
- `src/keyboards.js` — pure versioned keyboard store with independent draft/published snapshots, selected-vendor profiles, validation and conflict checks. Exposes `BintyKeyboards` in browsers and CommonJS for Node.
- `tests/catalog.test.cjs` — 12 catalogue regression tests.
- `tests/keyboards.test.cjs` — 11 keyboard draft/publish, validation and isolation tests.
- `tests/shortcuts.test.cjs` — 14 speed shortcut tests: versioning, validation, visibility, immutability and area isolation.
- `tests/demo.test.cjs` — 8 static demo wiring and syntax checks.
- `tests/ui-smoke.test.cjs` — 12 Node VM integration scenarios (authored, CI execution not independently verified).
- `openapi.yaml` — proposed REST v1 contract; no API server exists.
- `ARCHITECTURE.md`, `ROADMAP.md`, `STATUS.md`, `CHANGELOG.md` — architectural constraints, work queue and checkpoints.

## Test locally
Requires Node 20+ and Python 3.11+ (Python 3.13 in GitHub Actions). Run `node --test tests/*.test.cjs` for the browser/demo suite and `python3 -m unittest discover -s tests -p 'test_*.py' -v` for the SQLite modules. The Pages workflow gates deployment on **both** suites. The last independently observed Node result was 146/146 passed for v0.2.8; the v0.2.9 SQLite adapter passed 13/13 locally; the **14 new v0.2.10 quote tests passed locally on Python 3.13.5**, and their committed Git blob hashes match the tested files. The v0.2.11 GitHub Actions gate passed 147/147 native Node tests and 39/39 Python tests on 2026-11-02; public browser/hardware checks remain outstanding. Do not infer deployment success from a GitHub commit.


## Offering proposal contract
`BintyOfferings.createStore(products)` owns in-memory published products and pending per-product proposals. An outlet manager may propose name, availability or price changes only for their outlet. Only the venue-admin role may approve/publish or reject. Published products increment versions; stale versions fail closed and events are recorded in a defensive-copy audit log. In the future API, prices are represented as integer GBP pence (`priceMinor`), whereas the browser demo currently uses pound-number prices. The conversion and rounding must occur in a validated server adapter. Proposed API endpoints are in `openapi.yaml`, not running.

## Catalogue contract
`BintyCatalog.project(products, {areaMode, outlet, category, search, channel})` returns a non-mutating filtered view. `areaMode` can be `All`, `Short Menu`, a vendor name, or an array of allowed vendor names. `outlet` is a staff-only navigation filter: guest channel ignores it but still obeys the area policy. `categories` and `outlets` derive navigation from the same allowed products. These functions are **display filters**, not permissions. Server-side identity and access rules are required before real use.

## Keyboard publishing contract
A selling area has a published profile (`all`, `short`, or selected `vendors`) with a monotonically increasing version. A manager can stage an unpublished draft, discard it, or publish it against an expected current version. The till and QR always read the published profile. The demo stores these versions only in browser memory; no server, multi-user conflict handling, persistence or secure manager permissions exists. The proposed REST endpoints and future bearer-auth boundary are specified in `openapi.yaml`.

## Staff speed-key contract (v0.2.3)\n`BintyShortcuts.createStore(initial,{areas,products})` manages in-memory per-area shortcut drafts and published versions. `visible(products,areaMode,profile,BintyCatalog)` intersects published favourites/categories with the **currently published** area keyboard. Staff favourites add a product with one touch through the existing demo stock-checked `add()` handler; a category jump selects the category and returns to the all-outlet folder. This is presentation-only, not permission enforcement. The proposed `/api/v1/venues/{venueId}/areas/{areaId}/shortcuts` endpoints are documentation, not running services.\n\n## API and extension policy
The intended public integration contract is versioned under `/api/v1` in `openapi.yaml`. Future clients (bar tills, guest QR, outlet consoles, kitchen screens, Claude-built tools) must use published contracts, not reach into each other's UI state. All price changes, checkout, payments, inventory and vendor accounting must eventually be validated and committed by a server.

For agent contributions: read STATUS and ROADMAP first, pick one bounded feature, add tests, run them, update CHANGELOG and STATUS with evidence and a rollback commit, and avoid overwriting concurrent work. No force pushes or credentials in the repository. Dojo remains the preferred planned payment processor, but this demo has **no Dojo, Spektrix, Zonal, live hardware, secure PIN login, stock transaction engine or real voucher integration**.

## Market reference
Toast separates saved menu edits from publishing to POS and online channels, and supports publish permissions; Square has a typed catalogue for items, variations, categories and modifiers. BintyPOS applies this pattern to configurable **venue areas** with independently managed vendor menus. BintyPOS adds separate outlet ownership and flexible area visibility within one shared venue:
- https://support.toasttab.com/en/article/Global-Publishing-Experience-in-Toast-Back-End
- https://support.toasttab.com/en/article/Toast-for-Restaurant-Retail-Ordering-of-POS-Buttons (Toast recommends a speed screen or manageable category for non-scannable items)
- https://developer.squareup.com/docs/catalog-api/design-a-catalog
