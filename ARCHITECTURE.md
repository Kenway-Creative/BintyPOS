# BintyPOS architecture | prototype v0.2.2

## Principle
One venue, many businesses, unlimited configurable selling areas. Businesses, tills, menus, stock pools and fulfilment stations are independent dimensions, linked by explicit identifiers. Never infer merchant ownership or stock source solely from a UI folder/category.

## Current state
The current static browser simulation uses index.html plus a pure, tested src/catalog.js module to project a shared catalogue into selling areas, staff outlet folders and QR views. Versioned keyboard profiles and drafts now live in the pure src/keyboards.js module; other state (cart, orders, stock and PINs) remains local and illustrative. No production security or backend. The other modules below are *proposals*, not implemented yet.

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
