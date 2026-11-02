# BintyPOS — Blackstock Market EPOS prototype

**Prototype v0.2.5** · public demonstration only · no live payments or merchant data.

BintyPOS is a modular, API-first concept for one venue containing many independently managed businesses. The goal is a fast bar till, flexible outlet keyboards, a shared basket and catalogue for staff and QR, reliable inventory, and auditable vendor reporting. It is **not** ready for trading.

## Run the demo
Open `index.html` using a local HTTP server (for example `python3 -m http.server 8000`) and visit `http://localhost:8000/`. GitHub Pages deploys through the GitHub Actions workflow in `.github/workflows/deploy.yml`, not branch-source publishing. A successful Pages deployment has not been independently verified.

Try: Main Bar → Pattersons folder → add Burger → Spuddy Hell folder → add Loaded Spud → one simulated checkout. Switching folders keeps the shared basket. Change the sales area to Pattersons and notice only that area's products and shortcuts appear. Guest QR reads the same catalogue but ignores staff-only folder selection. Back-office demo PINs are printed on screen and are **not secure**. On the staff till, try the **Speed keys** (Corona, Burger and Loaded Spud) for one-tap additions, or **Jump to category** (Food, Packaged, Cocktails) to navigate in one tap without losing the basket. Shortcuts are specific to the selected area and never appear on guest QR. As venue admin (demo PIN 2468), open **Back office → Published till keyboard**, choose Main Bar, select **Selected outlets**, toggle the desired vendors, and **Publish keyboard**. Draft changes remain invisible to staff and QR until publishing; the live version increments. Discard reverses an unpublished draft. In **Back office → Speed keys and category jumps**, select an area, stage up to eight favourite products and six category jumps, then publish; the till retains the old version until publication. Reload resets all profiles.

## Outlet offerings and central approval (v0.2.4)
Use **Back office** with an outlet demo PIN (Pattersons 1357, Spuddy Hell 8642, Cherry On Top 9753). Select one of that outlet's products, change its name, availability or price, then choose **Submit for approval**. The staff till and guest QR remain unchanged while the proposal is pending. Log out and enter venue admin demo PIN 2468 to view the **Venue approval queue**; approve and publish or reject the proposal. A successful publish increments the product version and updates the shared staff/QR catalogue. Rejection leaves the published catalogue unchanged.

All role checks, proposal history and approvals here run in **browser memory only**; client-side PINs and actor claims are insecure. Real API calls must derive identity and outlet scope server-side, require central approval, store audit events durably and reject stale revisions. **Prototype limitation:** basket snapshots and checkout revalidation are browser-only; real checkout must use server-issued quotes and atomic stock reservation.

## Basket price snapshots and review (v0.2.5)
When staff or a guest adds a product, BintyPOS captures the published product version, vendor, name and unit price in **integer GBP pence**. Existing basket totals are not silently recalculated when an outlet's price is approved. The basket shows a review warning when a product version, price, availability or ownership changes. A price/version conflict blocks simulated checkout until the operator deliberately clicks **Accept published prices**; an unavailable or removed product must be removed from the basket. The simulated order retains the accepted line-price snapshot for reporting.

To test: add Pattersons Burger (£12.50), use the Pattersons demo manager to propose £14.00, then approve with venue admin. Return to the till: the basket still shows £12.50, checkout is blocked, and accepting the revised price changes the basket to £14.00. All behaviour is local demo state and is **not a real price guarantee**.

`src/basket.js` is a pure CommonJS/browser module with immutable line snapshots, minor-unit totals, catalogue conflict detection, explicit repricing, and validated order snapshots. `tests/basket.test.cjs` contains 12 unit tests; the UI smoke tests include four basket scenarios. `tests/api-contract.test.cjs` checks the proposed quote API.

**Server boundary:** Real price quotes must be calculated from the authoritative catalogue, with server-side identity, availability, VAT, promotions, atomic inventory reservation and expiry. The proposed `/api/v1/venues/{venueId}/quotes` and explicit accept-prices endpoints are **specification only**. Dojo remains the preferred future payment provider, not connected.

## Source structure
- `index.html` — static touch demo, simulated transactions and illustrative products.
- `src/catalog.js` — pure, reusable catalogue projection for sales areas, outlet folders, category tabs and text search.
- `src/basket.js` — immutable per-line price snapshots, explicit review and integer-pence subtotals.
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
Requires Node 20 or newer. Run `node --test tests/*.test.cjs` from the repository root. The GitHub Pages workflow runs these tests **before** deploying the static demo. There are 93 committed test cases. **93/93 passed in a V8 Node-test compatibility harness**, including twelve VM smoke scenarios through a compatibility shim. Native Node CI and real browser testing have not been independently verified. This is not evidence of native Node CI or real browser/device testing. Native Node and Pages outcomes remain unconfirmed. If tests fail, deployment should stop. No package installation or external dependencies are needed.

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
