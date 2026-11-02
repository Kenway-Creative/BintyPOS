# BintyPOS status

Version: **0.2.1** — first functional catalogue module
Date: 2026-11-02
Canonical repository: Kenway-Creative/BintyPOS · main
Prior rollback baseline: `dbdb298f9e833777d9fe39a6194dcb3432572c9a`
Feature commit: `f22bf98c458a7786944b4e3474ed9497d016e54f`
Test-gated deploy workflow commit: `3d01cacebfee14b86fada127ad72c06acf5681fb`

## Completed
- Pure catalogue projection module shared by staff till and QR UI, with area policies, vendor folders, categories and search.
- Staff-only folder navigation does not alter basket; changing area resets filters.
- Added 12 catalogue regression tests and 3 static demo tests.
- GitHub Pages deployment workflow runs Node tests before artifact upload.

## Verification evidence
- 12 direct V8 assertions passed against the exact module source before committing.
- Inline application JavaScript parsed and 5 mocked-DOM UI smoke checks passed before committing.
- Node test files committed, but a real Node CI test run is **not yet independently confirmed**.
- GitHub Pages public deployment, live browser rendering and multi-device tests **not yet independently confirmed**.

## Limitations and blockers
- Browser memory only. All prices, inventory, order states and PINs are illustrative.
- No secure authentication, actual API server, stock reservations, Dojo/Spektrix integration, audited accounting or real payment processing.
- Area policies currently come from demo local configuration; production needs persisted, versioned published keyboards.
- UI is not a security boundary. Manager PINs are publicly displayed demonstration values.

## Next bounded feature
Build an editable, versioned area keyboard/profile model with an explicit publish step and tests, allowing Binty to configure a vendor-only, mixed-vendor or full-menu till without duplicating products. Preserve basket and current static demo behaviour.
