# BintyPOS architecture | prototype v0.2.0

## Principle
One venue, many businesses, unlimited configurable selling areas. Businesses, tills, menus, stock pools and fulfilment stations are independent dimensions, linked by explicit identifiers. Never infer merchant ownership or stock source solely from a UI folder/category.

## Current state
The current index.html is a single-file browser simulation with illustrative products, local state and demo PINs. No production security or backend. The modular design below is a *proposal*, not implemented yet.

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
