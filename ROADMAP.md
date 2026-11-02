# BintyPOS roadmap

## Product north star
Blackstock Market: one transaction across many businesses, each outlet managed within appropriate permissions, shared recipe stock and accurate vendor settlement, with minimal peak-time taps.

## Completed
- 0.2.0 framework architecture and proposed open API.
- 0.2.1 reusable staff/QR catalogue projection, outlet folder filtering and automated test gate.
- 0.2.2 versioned keyboard profiles, selected-vendor drafts, explicit publish/discard and V8 regression checks.\n- 0.2.3 per-area staff speed keys, category jumps, staged publish/discard and visibility intersection.

## Prioritised releases
- **0.2.4 next:** controlled outlet offering edits — scoped manager drafts, central price approval/publishing and clear audit event contract. This resolves the original scoping tension between outlet self-management and central price ownership.
- 0.3.x complete fast outlet navigation, reorderable shortcuts, accessibility and real device touch-path measurements.
- 0.4.x authenticated server scaffold, scoped outlet management and venue-level permissions.
- 0.5.x published menu catalogue via running API with change history.
- 0.6.x atomic multi-vendor checkout, recipe stock reservations and idempotent order ledger.
- 0.7.x kitchen routing, status changes and durable audit log.
- 0.8.x voucher/discount split, vendor settlement and finance exports.
- 0.9.x Dojo sandbox integration, failure handling and load testing.
- 1.0 only after operational, security, hardware, payment and acceptance gates.

## Open decisions
Who is merchant of record, settlements, VAT and discount allocation; exact Dojo models; server/offline architecture; outlet roles and price-change approvals; stockroom mapping; day-one Spektrix requirements; actual peak transaction profile.

## Benchmark for v0.2.3\nToast Retail recommends speed screens or manageable menu groups for fast access to non-scannable products (https://support.toasttab.com/en/article/Toast-for-Restaurant-Retail-Ordering-of-POS-Buttons). BintyPOS offers per-area speed keys that are filtered through the published multi-vendor keyboard and are not exposed to guest QR. No device timing measurements yet.\n\n## Market benchmark
Toast separates saved edits from publishing to POS and online ordering (https://support.toasttab.com/en/article/Global-Publishing-Experience-in-Toast-Back-End). Square's typed catalogue separates item variations and categories (https://developer.squareup.com/docs/catalog-api/design-a-catalog). BintyPOS additionally models *outlet ownership* independently from *area visibility*, so a bar till can sell a mix of vendor menus without copying their products.
