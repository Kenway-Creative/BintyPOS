# Changelog

## [0.2.1] — 2026-11-02
**Feature:** Shared catalogue projection for fast bar outlet folders and QR parity.
- Extracted pure `src/catalog.js` module for sales-area policy, outlet shortcuts, category tabs, search and channel-aware filtering.
- Staff tills show only outlets allowed by the selected area; guest QR ignores staff navigation folders but respects the area restriction.
- Area changes reset folder/search filters while preserving the multi-vendor basket.
- Added 12 Node catalogue tests and 3 static-demo checks; GitHub Pages workflow now runs tests before deployment.
- Verification performed: 12 V8 module assertions, inline script parse and 5 simulated-DOM interaction checks. **Node GitHub Actions run and browser deployment not yet confirmed.**
- Implementation commits: `785fa59`, `2a27a72`, `f22bf98`, `760136c`, `3d01cac`.
- Rollback baseline: `dbdb298f9e833777d9fe39a6194dcb3432572c9a` (before feature). Do not force-push; revert offending commits or redeploy a verified checkpoint.

## [0.2.0] — 2026-11-02
- Architecture specification, proposed OpenAPI contract, roadmap, status and release process. API not yet implemented.

## [0.1.2] — prior
- Outlet shortcuts, manager demo PINs and back-office controls in browser-only simulation.

## Release policy
Keep every verified version in Git history. Tags/releases are not claimed until created and confirmed. Record exact commit hashes and limitations; never label a prototype as production-ready.
