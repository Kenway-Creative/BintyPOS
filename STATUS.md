# BintyPOS status

Version: **0.2.2** — published area keyboard profiles and draft editor
Date: 2026-11-02
Canonical repository: Kenway-Creative/BintyPOS · main
Rollback baseline (v0.2.1): `d3add5043483d7560f6ef6dde48283e41a6e96b7`
Keyboard module commit: `0528973f6c2ec3480551c5189a9ba33943cc5255`
Demo UI commit: `2b9151e28de583bf7e9da617b1d8e749bc586284`
API contract commit: `d7abce848cf907a2378e576bfbd973778947cf65`
Changelog checkpoint: `5a090fa3c2686e21bca8cafed6b288bc1f0341fa`

## Completed
- Pure, dependency-free `src/keyboards.js` for versioned selling-area profiles, unpublished drafts, explicit publish/discard, validation and optimistic version checks.
- Staff tills and QR read only published profiles. Venue-admin demo can configure all outlets, selected vendors or a short menu. Changing published area profiles does not clear a shared basket.
- Outlet demo managers cannot access keyboard configuration controls. Demo PINs are public, so this is UI-only separation.
- Proposed API endpoints for published keyboard, draft CRUD and version-checked publishing; no server exists.
- 12 catalogue tests, 11 keyboard tests and 5 static demo tests committed; GitHub Pages workflow runs `node --test tests/*.test.cjs` before deploying.

## Verification evidence
- Exact committed test source executed in a V8 compatibility shim for Node's `node:test`: **28/28 functions passed**. This is not a native Node test runner.
- Inline application JavaScript parsed and **10 mocked-DOM smoke checks passed**: draft invisibility, publish, outlet restriction, basket retention.
- Native Node CI outcome, public Pages deployment and real browser/device testing are **not independently confirmed**.

## Limitations and blockers
- Browser memory only; reload resets drafts, published profiles, orders and inventory.
- No authenticated backend, secure PIN, durable audit log, transactional stock, Dojo/Spektrix integration, or real payments.
- Price edits remain immediate demo changes, separate from keyboard publishing.
- Future server must enforce per-venue publish permissions, transactionally persist revisions, validate version headers, and sync devices.
- Market benchmark: Toast saved vs published configuration and publish permission: https://support.toasttab.com/en/article/Global-Publishing-Experience-in-Toast-Back-End

## Next bounded feature
Implement configurable staff till favourites and category shortcuts using the published keyboard profile, with tests that count taps for bar-to-outlet sales. Avoid changing order/payment behaviour.
