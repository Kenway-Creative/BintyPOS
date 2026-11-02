# BintyPOS roadmap

## Product north star
Blackstock Market: one transaction across many businesses, each outlet managed within appropriate permissions, shared recipe stock and accurate vendor settlement, with minimal peak-time taps.

## Completed
- 0.2.0 framework architecture and proposed open API.
- 0.2.1 reusable staff/QR catalogue projection, outlet folder filtering and automated test gate.

## Prioritised releases
- **0.2.2 next:** editable, versioned till profiles/keyboard layouts, supporting selected vendor combinations and explicit publishing; test that changes propagate to till and QR appropriately.
- 0.3.x fast outlet navigation, favourites, category shortcuts and measured touch paths.
- 0.4.x authenticated server scaffold, scoped outlet management and venue-level permissions.
- 0.5.x published menu catalogue via running API with change history.
- 0.6.x atomic multi-vendor checkout, recipe stock reservations and idempotent order ledger.
- 0.7.x kitchen routing, status changes and durable audit log.
- 0.8.x voucher/discount split, vendor settlement and finance exports.
- 0.9.x Dojo sandbox integration, failure handling and load testing.
- 1.0 only after operational, security, hardware, payment and acceptance gates.

## Open decisions
Who is merchant of record, settlements, VAT and discount allocation; exact Dojo models; server/offline architecture; outlet roles and price-change approvals; stockroom mapping; day-one Spektrix requirements; actual peak transaction profile.

## Market benchmark
Toast's menu hierarchy and POS button names/colours show the value of configured, staff-facing menus (https://doc.toasttab.com/doc/platformguide/adminCreatingYourMenuHierarchy.html). Square's typed catalogue separates item variations and categories (https://developer.squareup.com/docs/catalog-api/design-a-catalog). BintyPOS additionally models *outlet ownership* independently from *area visibility*, so a bar till can sell a mix of vendor menus without copying their products.
