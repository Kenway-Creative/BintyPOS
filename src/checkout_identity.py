"""BintyPOS v0.2.12: SQLite-scoped demo checkout capabilities, NOT staff login.

Only a trusted server/test fixture may call bootstrap_demo_identity or revoke_demo_identity.
No HTTP listener, real authentication, Dojo adapter, or client-side payment authority.
A checkout capability cannot authorise/confirm payment or commit stock.
"""
import hashlib
import secrets
import uuid

from order_lifecycle import SQLiteMockOrders
from persistent_reservations import ReservationError, _MAX


class ScopedDemoCheckout:
    """Narrow caller-facing facade around the *mock-only* SQLite order service.

    The caller supplies an opaque bearer credential, never a session identifier,
    ingredient demand, price, payment decision or venue role. Tokens are random,
    stored only as SHA-256 digests, venue-scoped, revocable and time-limited.
    This is a capability prototype; issuance is deliberately trusted-internal.
    """

    def __init__(self, path, now=None):
        self._orders = SQLiteMockOrders(path, now=now)
        with self._orders._transaction() as db:
            db.execute('''CREATE TABLE IF NOT EXISTS demo_checkout_capabilities (
                token_digest TEXT PRIMARY KEY, venue TEXT NOT NULL,
                session_id TEXT NOT NULL UNIQUE,
                channel TEXT NOT NULL CHECK(channel IN ('staff','qr')),
                expires_ms INTEGER NOT NULL, revoked INTEGER NOT NULL DEFAULT 0
                    CHECK(revoked IN (0,1)))''')

    @staticmethod
    def _digest(token):
        if not isinstance(token, str) or not 32 <= len(token) <= 256 or not token.isascii():
            raise ReservationError('CHECKOUT_UNAUTHENTICATED')
        return hashlib.sha256(token.encode('ascii')).hexdigest()

    def bootstrap_demo_identity(self, venue, channel, ttl_ms=900000):
        """TRUSTED TEST/BOOTSTRAP ONLY: never expose as an API endpoint."""
        self._orders._venue(venue)
        if channel not in ('staff', 'qr') or type(channel) is not str:
            raise ReservationError('INVALID_CHECKOUT_CHANNEL')
        if type(ttl_ms) is not int or not 1000 <= ttl_ms <= 900000:
            raise ReservationError('INVALID_CHECKOUT_TTL')
        now = self._orders._time()
        if now + ttl_ms > _MAX:
            raise ReservationError('INVALID_CHECKOUT_CLOCK')
        token = secrets.token_urlsafe(32)
        session = uuid.uuid4().hex
        with self._orders._transaction() as db:
            db.execute('INSERT INTO demo_checkout_capabilities VALUES(?,?,?,?,?,0)',
                       (self._digest(token), venue, session, channel, now + ttl_ms))
        return {'token': token, 'venue': venue, 'channel': channel, 'expiresAt': now + ttl_ms}

    def revoke_demo_identity(self, venue, token):
        """TRUSTED INTERNAL ONLY: do not expose as a public token-revocation route."""
        self._orders._venue(venue)
        digest = self._digest(token)
        with self._orders._transaction() as db:
            row = db.execute('SELECT venue FROM demo_checkout_capabilities WHERE token_digest=?',
                             (digest,)).fetchone()
            if not row or row['venue'] != venue:
                raise ReservationError('CHECKOUT_UNAUTHENTICATED')
            db.execute('UPDATE demo_checkout_capabilities SET revoked=1 WHERE token_digest=?',
                       (digest,))

    def _session(self, venue, token, action):
        self._orders._venue(venue)
        digest = self._digest(token)
        with self._orders._transaction() as db:
            row = db.execute('SELECT * FROM demo_checkout_capabilities WHERE token_digest=?',
                             (digest,)).fetchone()
            if not row or row['venue'] != venue or row['revoked'] or row['expires_ms'] <= self._orders._time():
                raise ReservationError('CHECKOUT_UNAUTHENTICATED')
            if action == 'cancel' and row['channel'] != 'staff':
                raise ReservationError('CHECKOUT_FORBIDDEN')
            return row['session_id']

    def create_quote(self, venue, token, lines):
        return self._orders.create_quote(venue, self._session(venue, token, 'quote'), lines)

    def accept_quote(self, venue, token, quote_id, expected_total_minor):
        return self._orders.accept_quote(venue, self._session(venue, token, 'accept'),
                                         quote_id, expected_total_minor)

    def create_order(self, venue, token, quote_id, key):
        return self._orders.create_order(venue, self._session(venue, token, 'order'),
                                         quote_id, key)

    def status_order(self, venue, token, order_id):
        return self._orders.status_order(venue, self._session(venue, token, 'status'), order_id)

    def cancel_mock(self, venue, token, order_id):
        return self._orders.cancel_mock(venue, self._session(venue, token, 'cancel'), order_id)
