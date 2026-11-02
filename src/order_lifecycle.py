"""BintyPOS v0.2.11: durable *mock-only* order/payment state proof of concept.

No HTTP listener, authenticated identity, real gateway, capture or money movement.
Session IDs are test fixtures. Never expose these internal methods to a browser.
"""
import json
import uuid
from trusted_checkout import TrustedQuoteReservations
from persistent_reservations import ReservationError


class MockPaymentAdapter:
    """Deterministic simulation, not a Dojo adapter or a real payment authorisation."""
    def __init__(self, approve=True, capture=True, void=True):
        self.approve = approve
        self.capture = capture
        self.void = void

    def authorise(self, order):
        return self.approve

    def complete(self, order):
        return self.capture

    def cancel(self, order):
        return self.void


class SQLiteMockOrders(TrustedQuoteReservations):
    """One SQLite file, atomic local state transitions and inventory movements.

    The mock adapter executes inside SQLite transactions ONLY because it cannot
    move money. A real provider needs a durable outbox and reconciliation instead.
    """
    def __init__(self, path, now=None, payment=None):
        super().__init__(path, now=now)
        if payment is not None and type(payment) is not MockPaymentAdapter:
            raise ValueError('Only the non-network MockPaymentAdapter is supported')
        self.payment = payment or MockPaymentAdapter()
        with self._transaction() as db:
            db.execute('''CREATE TABLE IF NOT EXISTS demo_orders (
                venue TEXT NOT NULL, order_id TEXT NOT NULL, session_id TEXT NOT NULL,
                quote_id TEXT NOT NULL, reservation_key TEXT NOT NULL,
                total_minor INTEGER NOT NULL, status TEXT NOT NULL,
                reason TEXT, created_ms INTEGER NOT NULL, updated_ms INTEGER NOT NULL,
                PRIMARY KEY(venue,order_id), UNIQUE(venue,quote_id),
                UNIQUE(venue,reservation_key))''')

    @staticmethod
    def _order(row):
        return {'orderId':row['order_id'], 'venue':row['venue'],
                'quoteId':row['quote_id'], 'reservationKey':row['reservation_key'],
                'totalMinor':row['total_minor'], 'status':row['status'],
                'reason':row['reason'], 'updatedAt':row['updated_ms']}

    def _load_order(self, db, venue, session, order_id):
        row = db.execute('SELECT * FROM demo_orders WHERE venue=? AND order_id=?',
                         (venue, order_id)).fetchone()
        if row is None:
            raise ReservationError('UNKNOWN_ORDER')
        if row['session_id'] != session:
            raise ReservationError('ORDER_SESSION_MISMATCH')
        return row

    def _refresh(self, db, row, now):
        if row['status'] in ('awaiting_payment', 'authorised'):
            self._expire(db, row['venue'], now)
            hold = self._get(db, row['venue'], row['reservation_key'])
            if not hold or hold['status'] != 'held':
                db.execute('''UPDATE demo_orders SET status='expired',reason='HOLD_NOT_ACTIVE',updated_ms=?
                              WHERE venue=? AND order_id=?''',
                           (now, row['venue'], row['order_id']))
                return self._load_order(db, row['venue'], row['session_id'], row['order_id'])
        return row

    def create_order(self, venue, session, quote_id, key):
        """Create a mock order from an accepted quote and its trusted stock hold.

        Hold creation precedes order insert; a crash between the two leaves a
        time-limited orphan hold, recoverable by replaying the same key.
        """
        self._venue(venue)
        self._session(session)
        self._quote_id(quote_id)
        self._key(key)
        self.reserve_accepted_quote(venue, session, quote_id, key)
        now = self._time()
        with self._transaction() as db:
            existing = db.execute('SELECT * FROM demo_orders WHERE venue=? AND quote_id=?',
                                  (venue, quote_id)).fetchone()
            if existing:
                if existing['reservation_key'] != key or existing['session_id'] != session:
                    raise ReservationError('ORDER_IDEMPOTENCY_CONFLICT')
                return self._order(self._refresh(db, existing, now))
            quote = self._load(db, venue, session, quote_id)
            hold = self._get(db, venue, key)
            if not hold or hold['status'] != 'held' or hold['expires_ms'] <= now:
                raise ReservationError('RESERVATION_NOT_ACTIVE')
            order_id = uuid.uuid4().hex
            db.execute('INSERT INTO demo_orders VALUES(?,?,?,?,?,?,?,?,?,?)',
                       (venue, order_id, session, quote_id, key, quote['total_minor'],
                        'awaiting_payment', None, now, now))
            return self._order(self._load_order(db, venue, session, order_id))

    def status_order(self, venue, session, order_id):
        self._venue(venue)
        self._session(session)
        self._quote_id(order_id)
        with self._transaction() as db:
            row = self._load_order(db, venue, session, order_id)
            return self._order(self._refresh(db, row, self._time()))

    def authorise_mock(self, venue, session, order_id):
        """Mock decision only; cannot authorise a card or move funds."""
        self._venue(venue)
        self._session(session)
        self._quote_id(order_id)
        with self._transaction() as db:
            now = self._time()
            row = self._refresh(db, self._load_order(db, venue, session, order_id), now)
            if row['status'] == 'authorised':
                return self._order(row)
            if row['status'] != 'awaiting_payment':
                raise ReservationError('ORDER_INVALID_TRANSITION')
            approved = self.payment.authorise(self._order(row))
            status = 'authorised' if approved else 'failed'
            if not approved:
                db.execute("UPDATE reservations SET status='released' WHERE venue=? AND key=? AND status='held'",
                           (venue, row['reservation_key']))
            db.execute('UPDATE demo_orders SET status=?,reason=?,updated_ms=? WHERE venue=? AND order_id=?',
                       (status, None if approved else 'MOCK_DECLINED', now, venue, order_id))
            return self._order(self._load_order(db, venue, session, order_id))

    def complete_mock(self, venue, session, order_id):
        """Simulated completion and atomic inventory movement; NO real capture."""
        self._venue(venue)
        self._session(session)
        self._quote_id(order_id)
        with self._transaction() as db:
            now = self._time()
            row = self._refresh(db, self._load_order(db, venue, session, order_id), now)
            if row['status'] == 'confirmed':
                return self._order(row)
            if row['status'] != 'authorised':
                raise ReservationError('ORDER_INVALID_TRANSITION')
            key = row['reservation_key']
            hold = self._get(db, venue, key)
            if not hold or hold['status'] != 'held':
                raise ReservationError('RESERVATION_NOT_ACTIVE')
            demands = json.loads(hold['demands'])
            for ingredient, qty in demands.items():
                stock = db.execute('SELECT qty FROM stock WHERE venue=? AND ingredient=?',
                                   (venue, ingredient)).fetchone()
                if not stock or stock['qty'] < qty:
                    db.execute("UPDATE reservations SET status='conflicted' WHERE venue=? AND key=?", (venue, key))
                    db.execute("UPDATE demo_orders SET status='needs_reconciliation',reason='STOCK_CONFLICT',updated_ms=? WHERE venue=? AND order_id=?",
                               (now, venue, order_id))
                    return self._order(self._load_order(db, venue, session, order_id))
            if not self.payment.complete(self._order(row)):
                db.execute("UPDATE demo_orders SET status='needs_reconciliation',reason='MOCK_CAPTURE_UNKNOWN',updated_ms=? WHERE venue=? AND order_id=?",
                           (now, venue, order_id))
                return self._order(self._load_order(db, venue, session, order_id))
            for ingredient, qty in demands.items():
                result = db.execute('UPDATE stock SET qty=qty-? WHERE venue=? AND ingredient=? AND qty>=?',
                                    (qty, venue, ingredient, qty))
                if result.rowcount != 1:
                    raise ReservationError('RESERVATION_STOCK_CONFLICT')
                db.execute('INSERT INTO movements VALUES(?,?,?,?)', (venue, key, ingredient, qty))
            db.execute("UPDATE reservations SET status='committed',committed_ms=? WHERE venue=? AND key=?", (now, venue, key))
            db.execute("UPDATE demo_orders SET status='confirmed',updated_ms=? WHERE venue=? AND order_id=?", (now, venue, order_id))
            return self._order(self._load_order(db, venue, session, order_id))

    def cancel_mock(self, venue, session, order_id):
        self._venue(venue)
        self._session(session)
        self._quote_id(order_id)
        with self._transaction() as db:
            now = self._time()
            row = self._refresh(db, self._load_order(db, venue, session, order_id), now)
            if row['status'] == 'released':
                return self._order(row)
            if row['status'] not in ('awaiting_payment', 'authorised'):
                raise ReservationError('ORDER_INVALID_TRANSITION')
            if row['status'] == 'authorised' and not self.payment.cancel(self._order(row)):
                db.execute("UPDATE demo_orders SET status='needs_reconciliation',reason='MOCK_VOID_UNKNOWN',updated_ms=? WHERE venue=? AND order_id=?",
                           (now, venue, order_id))
            else:
                db.execute("UPDATE reservations SET status='released' WHERE venue=? AND key=? AND status='held'", (venue, row['reservation_key']))
                db.execute("UPDATE demo_orders SET status='released',updated_ms=? WHERE venue=? AND order_id=?", (now, venue, order_id))
            return self._order(self._load_order(db, venue, session, order_id))
