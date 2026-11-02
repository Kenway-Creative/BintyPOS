# BintyPOS roadmap

## Product north star
Blackstock Market: one transaction across many businesses, each outlet managed within appropriate permissions, shared recipe stock and accurate vendor settlement, with minimal peak-time taps.

## Completed
- 0.2.0 framework architecture and proposed open API.
- 0.2.1 reusable staff/QR catalogue projection, outlet folder filtering and automated test gate.
- 0.2.2 versioned keyboard profiles, selected-vendor drafts, explicit publish/discard and V8 regression checks.\n- 0.2.3 per-area staff speed keys, category jumps, staged publish/discard and visibility intersection.

- 0.2.4 scoped outlet offering proposals, central price approval, version checks and demo audit history.

## Prioritised releases
- **0.2.5 next:** immutable basket line-price snapshots and checkout revalidation, so catalogue price changes cannot silently reprice orders already in progress. Add regression tests and future API contracts.
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

## Open decisions
Who is merchant of record, settlements, VAT and discount allocation; exact Dojo models; server/offline architecture; outlet roles and price-change approvals; stockroom mapping; day-one Spektrix requirements; actual peak transaction profile.

## Benchmark for v0.2.3\nToast Retail recommends speed screens or manageable menu groups for fast access to non-scannable products (https://support.toasttab.com/en/article/Toast-for-Restaurant-Retail-Ordering-of-POS-Buttons). BintyPOS offers per-area speed keys that are filtered through the published multi-vendor keyboard and are not exposed to guest QR. No device timing measurements yet.\n\n## Market benchmark
Toast separates saved edits from publishing to POS and online ordering (https://support.toasttab.com/en/article/Global-Publishing-Experience-in-Toast-Back-End). Square's typed catalogue separates item variations and categories (https://developer.squareup.com/docs/catalog-api/design-a-catalog). BintyPOS additionally models *outlet ownership* independently from *area visibility*, so a bar till can sell a mix of vendor menus without copying their products.
