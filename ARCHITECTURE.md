# BintyPOS architecture | prototype v0.2.6

## Principle
One venue, many businesses, unlimited configurable selling areas. Businesses, tills, menus, stock pools and fulfilment stations are independent dimensions, linked by explicit identifiers. Never infer merchant ownership or stock source solely from a UI folder/category.

## Current state
The current static browser simulation uses index.html plus a pure, tested src/catalog.js module to project a shared catalogue into selling areas, staff outlet folders and QR views. Per-area favourites and category jumps now live in `src/shortcuts.js`; versioned keyboard profiles and drafts live in the pure src/keyboards.js module; other state (cart, orders, stock and PINs) remains local and illustrative. No production security or backend. The other modules below are *proposals*, not implemented yet.

## Proposed modules
- Catalog: stable products, versions, modifiers, prices, vendor ownership and visibility rules.
- Presentation: bar folders, shortcuts, context-specific fast keyboards and guest QR projections from shared catalog.
- Orders: cart, validation, immutable snapshots, atomic stock reservations, idempotency keys, fulfilment splits and payment state transitions.
- Inventory: ingredient catalog, recipe versions, stock movements, shared virtual pools, physical count locations and count sessions.
- Finance: vendor attribution, discounts, vouchers, tax, refunds and settlement ledger.
- Identity: separately authenticated managers with server-enforced scope and permissions; no client PIN as a security boundary.
- Integrations: adapters for Dojo, Spektrix, printers and export/import.
- Reporting: permissioned materialized views derived from immutable transactions.

## API design
Contract-first REST versioned under /api/v1, documented in openapi.yaml. Design contract only; no running API server yet. API consumers are staff till, QR, vendor screens and back office. Financial and stock writes must be server-side transactions.

## Security and reliability gates
Never expose Dojo secrets in browser clients. Demo PINs are public and insecure; replace with genuine identity and role policy before any operational deployment. Concurrent stock updates must be atomic. Receipts and refunds must be idempotent. Offline mode must restrict finite-stock checkout when disconnected unless a safe reservation allocation exists. Prove peak throughput with a measured Blackstock load profile.

## Implemented catalogue boundary (v0.2.1)
`src/catalog.js` has no DOM or persistence dependencies and can be exercised in Node. `project(products, {areaMode, outlet, category, search, channel})` filters products without mutating source data. Staff outlet navigation never grants access to products excluded by the sales-area policy. Guest views ignore the staff-only folder but still respect area visibility. Categories and outlet shortcuts derive from the same projection. Area modes currently support All, a demo Short Menu, one vendor, or an array of vendors.

These are **presentation rules only**; they are not an authorisation implementation. Real API responses must be filtered server-side by authenticated venue/outlet scope and published menu version. Price, stock, and payment writes must not rely on browser projections.

## Implemented keyboard boundary (v0.2.2)
`src/keyboards.js` owns in-memory published area profiles (version starts at 1), optional drafts with baseVersion, publish/discard actions, input validation and defensive copies. Allowed vendor lists are checked against the demo vendor catalogue; publishing requires the expected version. All tills and QR projections call `liveAreaMode()`, which reads **published**, not draft, data. The back-office venue-admin demo screen can configure All, Short Menu or a subset of outlets without cloning product records. Outlet demo managers cannot edit area keyboards.

This is a *local prototype*, not a durable publish service. A production server must enforce venue-wide publishing permission, persist draft and published revisions transactionally, expose ETags or equivalent optimistic locking, audit actor/time and notify devices to sync. Client-side PINs and profile filters are not security boundaries. Product-price demo edits still take effect immediately and are not covered by keyboard publishing.

## Implemented speed-key boundary (v0.2.3)
`src/shortcuts.js` is a pure in-memory store for ordered per-area favourite product IDs (maximum eight) and category jumps (maximum six). Staged drafts never change published till buttons. Published shortcut versions increment with optimistic conflict checks; defensive snapshots prevent UI mutation of the store. `visible(products, areaMode, profile, BintyCatalog)` intersects favourite products and category jumps with the **published** area keyboard. Staff can add a favourite directly or jump to a category while preserving the shared basket. Guest QR has no staff speed keys. In the demo, direct add rechecks published visibility and the existing stock guard; neither is a secure checkout rule.
A future server must authenticate manager changes, atomically publish revisions, reject stale edits, preserve an audit trail and distribute versions to connected devices. The shortcut API is specified in `openapi.yaml` but not implemented.


## Implemented offering proposal boundary (v0.2.4)
`src/offerings.js` holds versioned published product snapshots, one pending proposal per product and an append-only *in-memory* event sequence. It accepts only name, price and availability edits. Outlet managers can stage proposals only for their own outlet; venue admins approve/publish or reject. The published staff/QR catalogue updates only after approval. Approval compares the expected product version and rejects stale or missing proposals. Unavailability is revalidated during demo checkout. All UI actor claims are **untrusted**; client PINs do not enforce production access. Published price changes no longer silently recalculate existing basket totals: the v0.2.5 basket module stores immutable line prices and blocks checkout until explicit review. This remains browser-only; production still requires authoritative server-issued quotes and atomic stock reservations.

The proposed API uses integer `priceMinor` (GBP pence), unlike demo pound-number prices. Server adapters must perform exact conversion and apply tenant/role checks, durable revision history, immutable audit events, idempotent publication and device invalidation. The prototype does **not** implement this backend. Role boundaries and publish approval must be validated against real staff policy before rollout.

## Implemented basket snapshot boundary (v0.2.5)
`src/basket.js` stores one immutable price/name/vendor/version snapshot per product ID when first added, with mutable quantity and integer GBP-pence subtotal. Re-adding the same product does not silently update its price. `review(publishedProducts)` reports product version, price or ownership changes, withdrawal and removal; `validatedOrder()` fails closed when conflicts remain. The UI shows the original basket total and an explicit **Accept published prices** action for changed but still-available products. Simulated checkout snapshots the accepted prices into the order record. A catalogue change made after checkout cannot rewrite historical line totals.

The browser still owns all state, so these checks are **not** a payment or pricing guarantee. A real API must create server-authoritative quotes with expiry, signed/versioned identity, tax/discount calculations, stock reservations and idempotency; never trust client-supplied prices or allow client-controlled PINs to grant authorisation. Proposed quote and acceptance endpoints are documented in `openapi.yaml`. In particular, acceptance must compare quote revisions, recheck catalogue/availability, and record who accepted a new price. For any real Dojo payment attempt, payment state must be coordinated with order/stock commits to avoid double charging and duplicate tickets.

## Implemented aggregate inventory preflight (v0.2.6)
`src/inventory.js` is a pure, dependency-free browser/CommonJS module. It validates integer recipe and stock units, aggregates demands for every order line across businesses, identifies all shortages, and returns a new stock snapshot on success. It never mutates the input stock and refuses any deduction if one ingredient is short. Both staff and guest QR use the same add and checkout paths. The product tile's remaining quantity now accounts for ingredients already committed to the current basket, including other products' recipes.

This is a **single-browser synchronous demonstration** only. It is not safe for simultaneous devices, cannot prevent races, and does not represent a durable stock ledger or reservation. Real service requirements: authenticated tenant/stock-pool boundaries; recipe version snapshots; units of measure and yield; per-location physical counts; database transactions with row locks or equivalent atomic compare-and-reserve; idempotency; release on payment failure; immutable adjustments; offline reconciliation; inventory revision tracking and load tests. Never deduct stock based on client-provided ingredient counts. The proposed inventory preflight endpoint is advisory; successful preflight is not a reservation.

Reference: Square Inventory API tracks state transitions and batch inventory changes atomically; its public documentation also notes limitations around ingredient/subcomponent tracking. BintyPOS's differentiator is combined ingredient demand across independently owned food and drink outlets sharing a single venue stock pool, not a claim of equivalent operational guarantees.
- https://developer.squareup.com/docs/inventory-api/how-it-works
- https://developer.squareup.com/docs/inventory-api/what-it-does
