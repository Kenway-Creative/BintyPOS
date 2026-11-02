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
- 16/16 reservation unit tests passed under native Node in an isolated local copy.
- Application JS parsed; three mocked-DOM V8 integration scenarios passed before commit.
- Full GitHub Actions and Pages deployment of v0.2.8 pending verification. Prior v0.2.7 Pages workflow at `30aa731...` succeeded on 2026-11-02.

## Limitations
- Browser-only state: separate tills can oversell. The demo commits immediately without card authorisation.
- Real service needs transactional DB locks, durable idempotency/expiry, stock movements, authenticated actors and payment reconciliation.
- PINs remain insecure demonstrations. No Dojo, Spektrix or real card payments.

## Next bounded feature
**0.2.9 — transactional persistence proof-of-concept** for competing clients and durable idempotency, keeping the static demo separate.

## Market comparison
Square documents atomic inventory batches and idempotency; BintyPOS demonstrates temporary recipe holds in local memory only. https://developer.squareup.com/docs/inventory-api/how-it-works
