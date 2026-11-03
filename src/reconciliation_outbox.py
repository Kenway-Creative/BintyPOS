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


    def record_manual_decision(self, venue, order_id, actor, decision, reason, request_key):
        """Append a mock-only human review note; never mutate orders or payments.

        Caller must be trusted maintenance code. Actor is an unverified label,
        not an authenticated identity. Reusing a request key is idempotent only
        for an identical payload; conflicting replays are rejected.
        """
        self._venue(venue)
        for value in (order_id, actor, reason, request_key):
            if not isinstance(value, str) or not value.strip() or len(value) > 512:
                raise ValueError('INVALID_AUDIT_FIELD')
        if decision not in ('investigate', 'escalate', 'acknowledge'):
            raise ValueError('INVALID_DECISION')
        with self._transaction() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS mock_reconciliation_decisions (
                venue TEXT NOT NULL, request_key TEXT NOT NULL,
                order_id TEXT NOT NULL, actor TEXT NOT NULL,
                decision TEXT NOT NULL, reason TEXT NOT NULL,
                recorded_ms INTEGER NOT NULL,
                PRIMARY KEY(venue, request_key),
                FOREIGN KEY(venue, order_id) REFERENCES mock_reconciliation_outbox(venue, order_id))""")
            pending = db.execute("""SELECT 1 FROM mock_reconciliation_outbox
                WHERE venue=? AND order_id=?""", (venue, order_id)).fetchone()
            if pending is None:
                raise ValueError('UNKNOWN_RECONCILIATION_ENTRY')
            existing = db.execute("""SELECT * FROM mock_reconciliation_decisions
                WHERE venue=? AND request_key=?""", (venue, request_key)).fetchone()
            if existing:
                if (existing['order_id'], existing['actor'], existing['decision'], existing['reason']) != (order_id, actor, decision, reason):
                    raise ValueError('AUDIT_IDEMPOTENCY_CONFLICT')
            else:
                db.execute("""INSERT INTO mock_reconciliation_decisions
                    (venue,request_key,order_id,actor,decision,reason,recorded_ms)
                    VALUES(?,?,?,?,?,?,?)""",
                    (venue, request_key, order_id, actor, decision, reason, self._time()))
            return [dict(row) for row in db.execute("""SELECT order_id AS orderId,
                actor, decision, reason, request_key AS requestKey,
                recorded_ms AS recordedAt FROM mock_reconciliation_decisions
                WHERE venue=? AND order_id=? ORDER BY recorded_ms, request_key""",
                (venue, order_id))]

    def list_manual_decisions(self, venue, order_id):
        """Read audit notes without triggering a payment or state transition."""
        self._venue(venue)
        with self._transaction() as db:
            exists = db.execute("""SELECT name FROM sqlite_master WHERE type='table'
                AND name='mock_reconciliation_decisions'""").fetchone()
            if not exists:
                return []
            return [dict(row) for row in db.execute("""SELECT order_id AS orderId,
                actor, decision, reason, request_key AS requestKey,
                recorded_ms AS recordedAt FROM mock_reconciliation_decisions
                WHERE venue=? AND order_id=? ORDER BY recorded_ms, request_key""",
                (venue, order_id))]
