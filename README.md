# BintyPOS — Blackstock Market EPOS prototype

**Prototype v0.2.1** · public demonstration only · no live payments or merchant data.

BintyPOS is a modular, API-first concept for one venue containing many independently managed businesses. The goal is a fast bar till, flexible outlet keyboards, a shared basket and catalogue for staff and QR, reliable inventory, and auditable vendor reporting. It is **not** ready for trading.

## Run the demo
Open `index.html` using a local HTTP server (for example `python3 -m http.server 8000`) and visit `http://localhost:8000/`. GitHub Pages deploys through the GitHub Actions workflow in `.github/workflows/deploy.yml`, not branch-source publishing. A successful Pages deployment has not been independently verified.

Try: Main Bar → Pattersons folder → add Burger → Spuddy Hell folder → add Loaded Spud → one simulated checkout. Switching folders keeps the shared basket. Change the sales area to Pattersons and notice only that area's products and shortcuts appear. Guest QR reads the same catalogue but ignores staff-only folder selection. Back-office demo PINs are printed on screen and are **not secure**.

## Source structure
- `index.html` — static touch demo, simulated transactions and illustrative products.
- `src/catalog.js` — pure, reusable catalogue projection for sales areas, outlet folders, category tabs and text search. Exposes `BintyCatalog` in browsers and CommonJS for Node.
- `tests/catalog.test.cjs` — 12 catalogue regression tests.
- `tests/demo.test.cjs` — static demo wiring and syntax checks.
- `openapi.yaml` — proposed REST v1 contract; no API server exists.
- `ARCHITECTURE.md`, `ROADMAP.md`, `STATUS.md`, `CHANGELOG.md` — architectural constraints, work queue and checkpoints.

## Test locally
Requires Node 20 or newer. Run `node --test tests/*.test.cjs` from the repository root. The GitHub Pages workflow runs these tests **before** deploying the static demo. If tests fail, deployment should stop. No package installation or external dependencies are needed.

## Catalogue contract
`BintyCatalog.project(products, {areaMode, outlet, category, search, channel})` returns a non-mutating filtered view. `areaMode` can be `All`, `Short Menu`, a vendor name, or an array of allowed vendor names. `outlet` is a staff-only navigation filter: guest channel ignores it but still obeys the area policy. `categories` and `outlets` derive navigation from the same allowed products. These functions are **display filters**, not permissions. Server-side identity and access rules are required before real use.

## API and extension policy
The intended public integration contract is versioned under `/api/v1` in `openapi.yaml`. Future clients (bar tills, guest QR, outlet consoles, kitchen screens, Claude-built tools) must use published contracts, not reach into each other's UI state. All price changes, checkout, payments, inventory and vendor accounting must eventually be validated and committed by a server.

For agent contributions: read STATUS and ROADMAP first, pick one bounded feature, add tests, run them, update CHANGELOG and STATUS with evidence and a rollback commit, and avoid overwriting concurrent work. No force pushes or credentials in the repository. Dojo remains the preferred planned payment processor, but this demo has **no Dojo, Spektrix, Zonal, live hardware, secure PIN login, stock transaction engine or real voucher integration**.

## Market reference
Toast supports menu/group/item hierarchy and configurable POS button names; Square has a typed catalogue for items, variations, categories and modifiers. BintyPOS adds separate outlet ownership and flexible area visibility within one shared venue:
- https://doc.toasttab.com/doc/platformguide/adminCreatingYourMenuHierarchy.html
- https://developer.squareup.com/docs/catalog-api/design-a-catalog
