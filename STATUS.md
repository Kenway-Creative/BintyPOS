# BintyPOS status

Version: **0.2.4** — scoped outlet offering drafts with central venue approval
Date: 2026-11-02
Canonical: Kenway-Creative/BintyPOS · main
Rollback baseline (v0.2.3): `19315ca624cefd6bffcb75370e132617179fbdbd`

## Completed
- `src/offerings.js`: pure, in-memory published product versions and one pending draft per product; outlet manager can stage only for their outlet; venue admin alone can approve/reject; optimistic version checks; defensive copies; event sequence.
- Back office proposal editor and venue approval queue. Product names, prices and availability remain unchanged for staff/QR until approval. Published availability is rechecked at simulated checkout.
- Removed direct price-edit handler; added proposed REST API endpoints and schemas in `openapi.yaml` (contract only, no server).
- Updated README, architecture, roadmap and changelog.

## Verification performed
- 73/73 committed test cases passed in a V8 compatibility harness, including 12 UI VM smoke scenarios using a lightweight VM substitute. This is **not** native Node execution or a real-browser test.
- Inline app JavaScript syntax parsed successfully in V8.
- Native GitHub Actions run, real browser, physical till and public GitHub Pages deployment **not independently confirmed**.
- Module commit: `ecf112a4d56205efac3344ce366159981ec5f072`
- Demo UI commit: `fdc0e8bbf6d88a6cb9986a396053b397392df867`
- Final checkout/availability fix: `7196fb9947f6cce4c384467578eb7145608fe11b`
- API contract: `02bcbb424281f84be943744c6a0ea86174271bf4`
- Test files: `ed6efe97c81c037c026efe7cf05ad7fec0bd866a`, `03c7daf050d252d4bc94c0589a25d437df3bbdba`, `09bcf9faaf3e550bad7082f30798a3b34fe9e485`

## Risks
- Demo PINs and actor claims are client-controlled and **not secure**; backend must authenticate and authorise every operation.
- Drafts, audit events, prices and orders live in one browser session; reload resets state.
- Current cart price is calculated from the latest catalogue. Publishing a price change while a basket is open can reprice it without explicit consent. Do not use for live trading.
- No durable audit, payments, Dojo, Spektrix, Zonal, merchant settlement, inventory concurrency or operational load proof.
- API specifies `priceMinor` as GBP pence; browser demo uses floating pound amounts. Conversion needs a server adapter.

## Next bounded feature
**0.2.5 — Immutable basket price snapshots and checkout revalidation** to prevent published price changes from silently repricing in-progress orders. Add unit and UI regression tests and a proposed API contract for basket line versions.

## Market comparison
Toast menu manager has distinct edit and publishing permissions, including Local Menu Edit scope (official platform documentation checked 2026-11-02):
https://doc.toasttab.com/doc/platformguide/platformMenuManagerPermissions.html
BintyPOS currently requires central venue approval for outlet changes; final policy needs venue owner sign-off.
