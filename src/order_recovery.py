"""Mock-only deterministic recovery inspection for SQLite checkout (v0.2.13).

Trusted internal maintenance only. Never automatically resolve an ambiguous payment.
No network, payment gateway, or public HTTP endpoint.
"""
from order_lifecycle import SQLiteMockOrders
from persistent_reservations import ReservationError


class MockOrderRecovery(SQLiteMockOrders):
    def inspect_recovery(self, venue):
        """Expire elapsed holds and identify orphan/ambiguous records atomically.

        Safe to retry and call from competing maintenance workers. Active orphan
        holds remain reserved until TTL expiry; no payment state is inferred.
        """
        self._venue(venue)
        now = self._time()
        with self._transaction() as db:
            self._expire(db, venue, now)
            # Only order-linked holds can affect an existing order state.
            db.execute("""UPDATE demo_orders SET status='expired',
                          reason='HOLD_NOT_ACTIVE', updated_ms=?
                          WHERE venue=? AND status IN ('awaiting_payment','authorised')
                          AND EXISTS (
                            SELECT 1 FROM reservations r
                            WHERE r.venue=demo_orders.venue
                              AND r.key=demo_orders.reservation_key
                              AND r.status!='held')""", (now, venue))
            orphans = [dict(r) for r in db.execute("""
                SELECT q.quote_id AS quoteId, q.reservation_key AS reservationKey,
                       r.status AS reservationStatus, r.expires_ms AS expiresAt
                FROM trusted_quotes q JOIN reservations r
                  ON r.venue=q.venue AND r.key=q.reservation_key
                LEFT JOIN demo_orders o ON o.venue=q.venue AND o.quote_id=q.quote_id
                WHERE q.venue=? AND o.order_id IS NULL
                ORDER BY q.quote_id""", (venue,))]
            ambiguous = [dict(r) for r in db.execute("""
                SELECT order_id AS orderId, reason, status
                FROM demo_orders WHERE venue=? AND status='needs_reconciliation'
                ORDER BY order_id""", (venue,))]
            return {'venue': venue, 'orphanHolds': orphans,
                    'needsManualReconciliation': ambiguous,
                    'checkedAt': now}
