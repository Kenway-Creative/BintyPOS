# BintyPOS — Blackstock Market EPOS prototype

**Prototype v0.2.3** · public demonstration only · no live payments or merchant data.

BintyPOS is a modular, API-first concept for one venue containing many independently managed businesses. The goal is a fast bar till, flexible outlet keyboards, a shared basket and catalogue for staff and QR, reliable inventory, and auditable vendor reporting. It is **not** ready for trading.

## Run the demo
Open `index.html` using a local HTTP server (for example `python3 -m http.server 8000`) and visit `http://localhost:8000/`. GitHub Pages deploys through the GitHub Actions workflow in `.github/workflows/deploy.yml`, not branch-source publishing. A successful Pages deployment has not been independently verified.

Try: Main Bar → Pattersons folder → add Burger → Spuddy Hell folder → add Loaded Spud → one simulated checkout. Switching folders keeps the shared basket. Change the sales area to Pattersons and notice only that area's products and shortcuts appear. Guest QR reads the same catalogue but ignores staff-only folder selection. Back-office demo PINs are printed on screen and are **not secure**. On the staff till, try the **Speed keys** (Corona, Burger and Loaded Spud) for one-tap additions, or **Jump to category** (Food, Packaged, Cocktails) to navigate in one tap without losing the basket. Shortcuts are specific to the selected area and never appear on guest QR. As venue admin (demo PIN 2468), open **Back office → Published till keyboard**, choose Main Bar, select **Selected outlets**, toggle the desired vendors, and **Publish keyboard**. Draft changes remain invisible to staff and QR until publishing; the live version increments. Discard reverses an unpublished draft. In **Back office → Speed keys and category jumps**, select an area, stage up to eight favourite products and six category jumps, then publish; the till retains the old version until publication. Reload resets all profiles.

## Source structure
- `index.html` — static touch demo, simulated transactions and illustrative products.
- `src/catalog.js` — pure, reusable catalogue projection for sales areas, outlet folders, category tabs and text search.
- `src/shortcuts.js` — pure per-area staff speed-key store with staged/published versions, validation and visibility intersection.
- `src/keyboards.js` — pure versioned keyboard store with independent draft/published snapshots, selected-vendor profiles, validation and conflict checks. Exposes `BintyKeyboards` in browsers and CommonJS for Node.
- `tests/catalog.test.cjs` — 12 catalogue regression tests.
- `tests/keyboards.test.cjs` — 11 keyboard draft/publish, validation and isolation tests.
- `tests/shortcuts.test.cjs` — 14 speed shortcut tests: versioning, validation, visibility, immutability and area isolation.
- `tests/demo.test.cjs` — 8 static demo wiring and syntax checks.
- `tests/ui-smoke.test.cjs` — 8 native Node VM integration scenarios (authored, CI execution not independently verified).
- `openapi.yaml` — proposed REST v1 contract; no API server exists.
- `ARCHITECTURE.md`, `ROADMAP.md`, `STATUS.md`, `CHANGELOG.md` — architectural constraints, work queue and checkpoints.

## Test locally
Requires Node 20 or newer. Run `node --test tests/*.test.cjs` from the repository root. The GitHub Pages workflow runs these tests **before** deploying the static demo. There are 53 committed test cases; this release directly exercised 45 tests in a V8 compatibility harness plus 10 mocked-DOM assertions. Native Node and Pages outcomes remain unconfirmed. If tests fail, deployment should stop. No package installation or external dependencies are needed.

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
