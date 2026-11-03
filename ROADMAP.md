# BintyPOS roadmap

## Product north star
Blackstock Market: one transaction across many businesses, each outlet managed within appropriate permissions, shared recipe stock and accurate vendor settlement, with minimal peak-time taps.

## Completed
- 0.2.0 framework architecture and proposed open API.
- 0.2.1 reusable staff/QR catalogue projection, outlet folder filtering and automated test gate.
- 0.2.2 versioned keyboard profiles, selected-vendor drafts, explicit publish/discard and V8 regression checks.\n- 0.2.3 per-area staff speed keys, category jumps, staged publish/discard and visibility intersection.

- 0.2.4 scoped outlet offering proposals, central price approval, version checks and demo audit history.
- 0.2.5 immutable GBP-pence basket snapshots, explicit catalogue-change review, checkout blocking and proposed server quote API.
- 0.2.6 shared recipe ingredient aggregation, basket-wide preflight and all-or-none browser stock consumption.
- 0.2.7 virtual stockroom categories, independent physical count locations, category reclassification, deterministic local consumption and stock tab demonstration.
- 0.2.8 idempotent in-memory stock holds, expiry/release, conflict detection and demo checkout integration.
- 0.2.9 standalone SQLite transaction proof-of-concept with durable holds, idempotency, movements and competing-client tests (no HTTP API).
- 0.2.10 trusted SQLite quote snapshots, explicit acceptance, product/recipe version invalidation, and atomic recipe-derived holds (no authenticated HTTP).
- 0.2.11 SQLite mock-only order state machine with persistent state, simulated authorisation/confirmation/cancellation, stock movements and reconciliation hold states; repaired stale OpenAPI CI assertion.
- 0.2.12 scoped demo checkout capability facade: server-generated token digests, venue/session binding, expiry/revocation, staff-only mock cancellation and no checkout payment authority (CI 148 Node + 52 Python passed).

- 0.2.13 mock-only transactional orphan-hold inspection, expiry and explicit ambiguous-outcome review; no automatic payment settlement.

- 0.2.14 SQLite capability validation and quote/order operations under one writer transaction, with nested savepoints and revocation concurrency tests.

## Prioritised releases
- **0.2.15 next:** durable mock-only outbox and reconciliation inspection, then verified human/device identity, outlet/area permissions and authenticated HTTP boundary; no real payments or unprotected routes.
- 0.3.x complete fast outlet navigation, reorderable shortcuts, accessibility and real device touch-path measurements.
- 0.4.x authenticated server scaffold, scoped outlet management and venue-level permissions.
- 0.5.x published menu catalogue via running API with change history.
- 0.6.x atomic multi-vendor checkout, recipe stock reservations and idempotent order ledger.
- 0.7.x kitchen routing, status changes and durable audit log.
- 0.8.x voucher/discount split, vendor settlement and finance exports.
- 0.9.x Dojo sandbox integration, failure handling and load testing.
- 1.0 only after operational, security, hardware, payment and acceptance gates.

## Benchmark for v0.2.4
Toast's menu manager separates edit and publish permissions; its Local Menu Edit role can be limited to local objects, while publishing requires a separate permission. Official reference (checked 2026-11-02): https://doc.toasttab.com/doc/platformguide/platformMenuManagerPermissions.html . BintyPOS prototype deliberately requires venue approval for *all* outlet proposals, including price; this stricter workflow reflects the central price-control brief but needs Binty/Mike sign-off.

## Benchmark for v0.2.7
Square's inventory API supports physical counts and stock adjustments associated with locations; its UK support documentation describes variance reporting and count reconciliation. BintyPOS additionally models a venue-wide virtual counting category that can aggregate quantities across physical positions, as required by Binty's scoping call. This is not a claim of Square-equivalent transactional or accounting capability. https://developer.squareup.com/docs/inventory-api/how-it-works and https://api.squareup.com/help/gb/en/article/8251-view-and-export-inventory-variance-report-with-square-for-retail

## Open decisions
Who is merchant of record, settlements, VAT and discount allocation; exact Dojo models; server/offline architecture; outlet roles and price-change approvals; stockroom mapping; day-one Spektrix requirements; actual peak transaction profile.

## Benchmark for v0.2.3\nToast Retail recommends speed screens or manageable menu groups for fast access to non-scannable products (https://support.toasttab.com/en/article/Toast-for-Restaurant-Retail-Ordering-of-POS-Buttons). BintyPOS offers per-area speed keys that are filtered through the published multi-vendor keyboard and are not exposed to guest QR. No device timing measurements yet.\n\n## Market benchmark
Toast separates saved edits from publishing to POS and online ordering (https://support.toasttab.com/en/article/Global-Publishing-Experience-in-Toast-Back-End). Square's typed catalogue separates item variations and categories (https://developer.squareup.com/docs/catalog-api/design-a-catalog). BintyPOS additionally models *outlet ownership* independently from *area visibility*, so a bar till can sell a mix of vendor menus without copying their products.

## Benchmark for v0.2.5
Square's Orders API uses a per-line `base_price_money` and quantity, and Toast recommends pricing/validating an order before submission through its `/orders/v2/prices` endpoint. BintyPOS v0.2.5 records the price shown when a line is added, blocks stale checkout and requires explicit acceptance before using a new published price. It is **not** a Square/Toast-compatible order engine and does not yet calculate VAT, discounts, stock reservations or live payment status.
- https://developer.squareup.com/reference/square/objects/orderlineitem
- https://doc.toasttab.com/doc/devguide/apiOrdersFirstOrder.html

## Benchmark for v0.2.6
Square Inventory API models inventory changes and atomic batches, but its documented Inventory API does not directly track ingredients/subcomponents. BintyPOS's local recipe preflight aggregates ingredient requirements across a multi-vendor basket and prevents local partial deductions; it is not an equivalent production inventory service. Checked 2026-11-02:
- https://developer.squareup.com/docs/inventory-api/how-it-works
- https://developer.squareup.com/docs/inventory-api/what-it-does

## Source-of-truth brief (reviewed 2026-11-02)
The attached `Hot Water Comedy Club x Access: Binty's ideal world` specifies virtual stockrooms that are *not physical rooms*, shared ingredients such as vodka, Prosecco, sugar and potatoes, and product recipes that deduct stock regardless of which selling area sold them. The scoping-call transcript confirms shared communal stock can be physically distributed throughout the building. Model logical pools independently of physical count locations; do not equate business/vendor or till with stock location.

## Benchmark v0.2.8
Square Inventory API documents atomic batched changes and an idempotency key (API version 2026-09-16). BintyPOS models recipe-based cross-vendor holds in one browser, **not** equivalent server guarantees. Checked 2026-11-02:
- https://developer.squareup.com/docs/inventory-api/how-it-works
- https://developer.squareup.com/reference/square/inventory-api/batch-change-inventory

## Benchmark for v0.2.9 (checked 2026-11-02)
Square's BatchChangeInventory API accepts an idempotency key and applies inventory changes atomically; see https://developer.squareup.com/reference/square/inventory-api/BatchChangeInventory and https://developer.squareup.com/docs/inventory-api/how-it-works . BintyPOS v0.2.9 demonstrates a **local database** transaction boundary for multi-ingredient stock holds and one-time movement commits, rather than claiming Square's production inventory capability. Its browser demo is not connected to this SQLite adapter.

## Deferred operational work
Production auth/permissions, accepted server quote, recipe version binding, order ledger, Dojo sandbox and reconciliation, migrations/backups, monitoring, multi-host transaction store, and realistic peak load testing remain required. The direct-demand adapter is only for trusted internal testing and must not be exposed as a public API.


## Benchmark for v0.2.12 (checked 2026-11-03)
Square documents OAuth scopes, short-lived tokens, least privilege, revocation and protected credentials: https://developer.squareup.com/docs/auth and https://developer.squareup.com/docs/oauth-api/best-practices . BintyPOS v0.2.12 uses only locally issued, hashed demo bearer capabilities for checkout fixtures, scoped to venue and channel; it does **not** implement Square OAuth, staff login, true identity verification, or production transport security.
