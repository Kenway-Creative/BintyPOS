"""Durable mock-only reconciliation queue. Trusted maintenance, no dispatcher."""
from order_recovery import MockOrderRecovery

class MockReconciliationOutbox(MockOrderRecovery):
    def __init__(self, path, now=None, payment=None):
        super().__init__(path, now=now, payment=payment)
        with self._transaction() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS mock_reconciliation_outbox (
                venue TEXT NOT NULL, order_id TEXT NOT NULL,
                reason TEXT NOT NULL, first_seen_ms INTEGER NOT NULL,
                last_seen_ms INTEGER NOT NULL,
                PRIMARY KEY(venue, order_id),
                FOREIGN KEY(venue, order_id) REFERENCES demo_orders(venue, order_id))""")

    def snapshot_pending(self, venue):
        """Atomically snapshot ambiguous mock outcomes; never resolve payments."""
        self._venue(venue)
        now = self._time()
        with self._transaction() as db:
            rows = db.execute("""SELECT order_id, reason FROM demo_orders
                WHERE venue=? AND status='needs_reconciliation'
                ORDER BY order_id""", (venue,)).fetchall()
            for row in rows:
                db.execute("""INSERT INTO mock_reconciliation_outbox
                    (venue,order_id,reason,first_seen_ms,last_seen_ms)
                    VALUES(?,?,?,?,?)
                    ON CONFLICT(venue,order_id) DO UPDATE SET
                    reason=excluded.reason, last_seen_ms=excluded.last_seen_ms""",
                    (venue, row['order_id'], row['reason'] or 'UNKNOWN', now, now))
            return [dict(row) for row in db.execute("""
                SELECT order_id AS orderId, reason, first_seen_ms AS firstSeenAt,
                    last_seen_ms AS lastSeenAt
                FROM mock_reconciliation_outbox WHERE venue=? ORDER BY order_id""", (venue,))]
