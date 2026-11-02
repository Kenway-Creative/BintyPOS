# BintyPOS status

Version: **0.2.11** — durable mock-only order/payment state lifecycle
Date: 2026-11-02
Canonical: Kenway-Creative/BintyPOS · main
Rollback baseline: `3394a2f0ad6650fa201406efd1e73faa7eee6601`

## Implemented
- SQLite mock order state: awaiting_payment, authorised, confirmed, failed, released, expired and needs_reconciliation. No real card authorisation or capture.
- Simulated confirmed order, ingredient movements and reservation commit in one SQLite transaction; idempotent replay and durable order history.
- Mock declines and cancellations release stock; unknown mock capture/void and stock conflicts require reconciliation.
- Fixed stale hardcoded 0.2.8 OpenAPI version assertion that blocked CI for 0.2.10 (run 41541876510 failed: 145/146 Node tests passed).

## Verification checkpoint
- New Python source syntax and 12 new lifecycle test cases added. Complete native GitHub Actions results for this commit must be checked; no claim of successful deployment before confirmation.
- Previous 0.2.10 CI failed in Node contract test, before running Python tests or Pages deployment.

## Limitations and blockers
- Session IDs are caller-provided fixtures, **not verified identity**; no authenticated server, HTTP routes or real payment provider. Only MockPaymentAdapter accepted; it cannot move money.
- The original browser demo is separate. The inherited `commit` method bypasses payment verification and is trusted-internal only.
- Crash between stock hold and order creation can leave a TTL-bounded orphan hold; a real payment provider needs an outbox and reconciliation instead of inline SQLite mock callbacks.
- Dojo preferred and required for planned payments, pending sandbox feasibility validation. No Spektrix payment claims.

## Next bounded feature
**0.2.12 — verified checkout identity and transactional order/outbox recovery scaffold.** Add server-issued identity/venue scope, safe retry/reconciliation of orphan holds and ambiguous mock outcomes before any HTTP or payment work.

## Market comparison
Square distinguishes authorised payments from completed/captured payments and prevents completing order fulfilments before payment. BintyPOS implements analogous state boundaries only in local mock simulation: https://developer.squareup.com/docs/orders-api/pay-for-orders
