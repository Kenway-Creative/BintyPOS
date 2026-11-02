# BintyPOS roadmap

## Product north star
Blackstock Market: one transaction across many businesses, every outlet controlled appropriately, shared recipes and stock, precise settlements, minimal friction at peak.

## Release gates
0.2.x modular source, schemas, tests and API contract (no real payments).
0.3.x area/outlet navigation with reusable menus, shortcuts and one-click return.
0.4.x back-office permissions model and authenticated server scaffold.
0.5.x unified menu publishing to till and QR.
0.6.x deterministic checkout, inventory ledger and atomic stock reservation.
0.7.x fulfilment/kitchen routing, order states and audit log.
0.8.x vouchers, promotions, vendor attribution and financial exports.
0.9.x Dojo sandbox integration, failover experiments and measured peak load.
1.0 launch candidate only after security, operational, payment and independent acceptance.

## Next implementation step
Extract pure catalog/outlet navigation logic and tests from index.html without breaking GitHub Pages demo. Then validate that any supported bar till can navigate into an outlet and back while preserving the basket.

## Open questions
Confirmed Dojo Pocket models and integration approval; vendor merchant-of-record and settlement rules; roles and edit permissions; handling of disconnected limited-stock orders; Zonal exports and notice; day-one Spektrix scope.

## Benchmarks
Toast supports hierarchies of menus, groups, subgroups and items; Square Catalog API defines items, variations, modifiers and categories. BintyPOS additionally requires vendor/area/stock pool separation within *one* venue, rather than assuming venue/location = business. Official references:
https://support.toasttab.com/en/article/Menus-Menu-Groups-and-Subgroups
https://developer.squareup.com/reference/square/catalog-api
