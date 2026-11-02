# BintyPOS status

Version: **0.2.3** — published staff speed keys and category jumps
Date: 2026-11-02
Canonical repository: Kenway-Creative/BintyPOS · main
Rollback baseline (v0.2.2): `178b3a9257a50d31afb046f88bb47083185bc82d`

## Completed
- Pure `src/shortcuts.js` store with per-area favourites (up to eight) and category jumps (up to six), unpublished drafts, publish/discard, version conflicts and defensive snapshots.
- Staff till one-tap favourites and category jumps filtered by the **published** area keyboard. Guest QR has no staff shortcuts. Basket survives navigation and publishing.
- Venue-admin demo editor for shortcut drafts; all PINs remain insecure demonstration values.
- Proposed OpenAPI shortcut endpoints; **no running backend**.

## Verification evidence
- **45/45** pure/static tests executed in a V8 Node-test compatibility harness.
- **10/10** mocked-DOM assertions passed: direct add, basket retention, category jump, area restrictions, draft and publish.
- **8** additional Node VM UI smoke tests authored and committed; native Node CI, live Pages and real-device checks **not independently confirmed**.
- Inline app JavaScript syntax checked.
- Implementation commits: `461d2456eaf2574b3dbbc696db78258c8cb8b885`, `c6712e62cd132c5313dca109680a46720cb28d33`.
- Tests: `caa01097127b01ba7a7924c1ca085a4b5bb48c8a`, `deec17cf733817331cf1c4694eb0a2bc7a70a35f`, `285366d8726a144dd8e6af9cc3935a1684b22b04`.
- API: `f0c8bfac851a808aa92797dc7fab9979e86150ed`.

## Risks and limitations
- Browser-memory-only simulation. No secure PIN/auth, durable audit log, transactional stock, real Dojo/Spektrix integration or real payments.
- Shortcut projection is a display rule, not authorisation. Server must enforce scope, publish permissions, checkout and stock.
- Touch-count reduction is a design property; service speed not measured on real tills.
- Binty's ideal-world requirements include r7 (fastest sellers on home screen) and r11 (central price control). Outlet managers' scope versus central pricing needs explicit approval policy.

## Next bounded feature
**0.2.4 — Outlet offering drafts with central price approval**. Define scoped edit permissions and audited approval/publish contract, keeping live catalogue immutable until authorised publication.

## Market comparison
Toast Retail recommends speed screens or manageable categories for fast non-scannable item access, per guidance reviewed 2026-11-02:
https://support.toasttab.com/en/article/Toast-for-Restaurant-Retail-Ordering-of-POS-Buttons
