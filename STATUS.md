# BintyPOS status

Version: **0.2.8** — in-memory shared-stock reservations
Date: 2026-11-02
Canonical: Kenway-Creative/BintyPOS · main
Rollback baseline (v0.2.7): `30aa731662bc9ba97ec7611762700e5077b5801c`

## Implemented
- `src/reservations.js` provides idempotent holds, expiry, release, conflict checks and adapter-based commit.
- Both staff and QR simulated checkout use the hold/commit path; physical stock is consumed only after commit.
- OpenAPI v0.2.8 proposes authenticated quote-derived reservations and service-only commit; **no running API**.

## Verification
- **146/146 full regression tests passed** under native Node 22 in GitHub Actions on 2026-11-02 at 21:12 UTC (run 41526203697). This includes 16 reservation unit tests, 3 new UI smoke tests, 1 static integration test and 1 API contract test.
- Application JavaScript parsed; three mocked-DOM V8 integration scenarios also passed before commit.
- GitHub Pages **Deploy Pages step succeeded** for v0.2.8 commit `9770d6d87cd2dde63856133972a5e28e92c2d28c`. Public live-browser inspection and real hardware tests remain unverified.
- CI: https://github.com/Kenway-Creative/BintyPOS/actions/runs/41526203697

## Limitations
- Browser-only state: separate tills can oversell. The demo commits immediately without card authorisation.
- Real service needs transactional DB locks, durable idempotency/expiry, stock movements, authenticated actors and payment reconciliation.
- PINs remain insecure demonstrations. No Dojo, Spektrix or real card payments.

## Next bounded feature
**0.2.9 — transactional persistence proof-of-concept** for competing clients and durable idempotency, keeping the static demo separate.

## Market comparison
Square documents atomic inventory batches and idempotency; BintyPOS demonstrates temporary recipe holds in local memory only. https://developer.squareup.com/docs/inventory-api/how-it-works
