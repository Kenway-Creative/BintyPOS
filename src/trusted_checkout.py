"""Trusted, non-network quote -> durable inventory hold prototype (v0.2.10).

All methods are INTERNAL service calls. Session IDs are caller-supplied test fixtures,
not authentication; publish_product is a trusted fixture/administration hook.
No payment, tax, VAT, discounts, API listener or live checkout exists.
"""
import json
import uuid
from persistent_reservations import SQLiteReservations, ReservationError, _demands, _valid_id, _MAX


def _json(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'))


def _positive(value):
    return type(value) is int and 0 < value <= _MAX


class TrustedQuoteReservations(SQLiteReservations):
    """Atomic quote issuance, explicit acceptance and recipe-derived stock holds."""

    def __init__(self, path, now=None):
        super().__init__(path, now=now)
        with self._transaction() as db:
            db.execute('''CREATE TABLE IF NOT EXISTS trusted_products (
                venue TEXT NOT NULL, product TEXT NOT NULL, business TEXT NOT NULL,
                price_minor INTEGER NOT NULL CHECK(price_minor >= 0),
                version INTEGER NOT NULL, available INTEGER NOT NULL,
                recipe TEXT NOT NULL, PRIMARY KEY(venue,product))''')
            db.execute('''CREATE TABLE IF NOT EXISTS trusted_quotes (
                venue TEXT NOT NULL, quote_id TEXT NOT NULL, session_id TEXT NOT NULL,
                lines TEXT NOT NULL, demands TEXT NOT NULL, total_minor INTEGER NOT NULL,
                versions TEXT NOT NULL, status TEXT NOT NULL CHECK(status IN ('draft','accepted')),
                created_ms INTEGER NOT NULL, expires_ms INTEGER NOT NULL,
                reservation_key TEXT, PRIMARY KEY(venue,quote_id),
                UNIQUE(venue,reservation_key))''')

    @staticmethod
    def _session(session):
        if not _valid_id(session):
            raise ReservationError('INVALID_CHECKOUT_SESSION')

    @staticmethod
    def _quote_id(quote_id):
        if not isinstance(quote_id, str) or len(quote_id) != 32 or any(c not in '0123456789abcdef' for c in quote_id):
            raise ReservationError('INVALID_QUOTE_ID')

    def publish_product(self, venue, product, business, price_minor, recipe, available=True):
        """Trusted fixture/admin operation, NOT a public route or user permission check."""
        self._venue(venue)
        if not _valid_id(product) or not _valid_id(business) or type(price_minor) is not int or not 0 <= price_minor <= _MAX or type(available) is not bool:
            raise ReservationError('INVALID_PUBLISHED_PRODUCT')
        recipe = _demands(recipe)
        with self._transaction() as db:
            old = db.execute('SELECT version FROM trusted_products WHERE venue=? AND product=?', (venue,product)).fetchone()
            version = old['version'] + 1 if old else 1
            db.execute('''INSERT INTO trusted_products VALUES(?,?,?,?,?,?,?)
                ON CONFLICT(venue,product) DO UPDATE SET business=excluded.business,
                price_minor=excluded.price_minor, version=excluded.version,
                available=excluded.available, recipe=excluded.recipe''',
                (venue,product,business,price_minor,version,int(available),_json(recipe)))
            return version

    @staticmethod
    def _quote_record(row):
        if row is None:
            return None
        return {'quoteId':row['quote_id'], 'venue':row['venue'], 'sessionId':row['session_id'],
                'lines':json.loads(row['lines']), 'totalMinor':row['total_minor'],
                'status':row['status'], 'expiresAt':row['expires_ms'],
                'reservationKey':row['reservation_key']}

    @staticmethod
    def _check_lines(lines):
        if not isinstance(lines,list) or not 1 <= len(lines) <= 100:
            raise ReservationError('INVALID_QUOTE_LINES')
        amounts = {}
        for line in lines:
            if not isinstance(line,dict) or set(line) != {'productId','quantity'} or not _valid_id(line['productId']) or not _positive(line['quantity']):
                raise ReservationError('INVALID_QUOTE_LINES')
            product = line['productId']
            amounts[product] = amounts.get(product,0) + line['quantity']
            if amounts[product] > _MAX:
                raise ReservationError('INVALID_QUOTE_LINES')
        return amounts

    @staticmethod
    def _fresh(db, row):
        for product, version in json.loads(row['versions']).items():
            current = db.execute('SELECT version,available FROM trusted_products WHERE venue=? AND product=?', (row['venue'],product)).fetchone()
            if not current or not current['available'] or current['version'] != version:
                raise ReservationError('STALE_QUOTE')

    def create_quote(self, venue, session, lines, ttl_ms=120000):
        self._venue(venue)
        self._session(session)
        amounts = self._check_lines(lines)
        if type(ttl_ms) is not int or not 1000 <= ttl_ms <= 900000:
            raise ReservationError('INVALID_QUOTE_TTL')
        now = self._time()
        if now + ttl_ms > _MAX:
            raise ReservationError('INVALID_QUOTE_CLOCK')
        with self._transaction() as db:
            total, demands, versions, snapshots = 0, {}, {}, []
            for product, qty in sorted(amounts.items()):
                row = db.execute('SELECT * FROM trusted_products WHERE venue=? AND product=?',(venue,product)).fetchone()
                if not row or not row['available']:
                    raise ReservationError('PRODUCT_UNAVAILABLE')
                amount = row['price_minor'] * qty
                if amount > _MAX-total:
                    raise ReservationError('QUOTE_AMOUNT_OVERFLOW')
                total += amount
                versions[product] = row['version']
                snapshots.append({'productId':product,'businessId':row['business'],
                                  'quantity':qty,'priceMinor':row['price_minor'],
                                  'version':row['version']})
                for ingredient, per_unit in json.loads(row['recipe']).items():
                    demand = per_unit * qty
                    demands[ingredient] = demands.get(ingredient,0) + demand
                    if demands[ingredient] > _MAX:
                        raise ReservationError('QUOTE_DEMAND_OVERFLOW')
            quote_id = uuid.uuid4().hex
            db.execute('INSERT INTO trusted_quotes VALUES(?,?,?,?,?,?,?,?,?,?,NULL)',
                (venue,quote_id,session,_json(snapshots),_json(demands),total,_json(versions),
                 'draft',now,now+ttl_ms))
            return self._quote_record(db.execute('SELECT * FROM trusted_quotes WHERE venue=? AND quote_id=?',(venue,quote_id)).fetchone())

    def _load(self, db, venue, session, quote_id):
        row = db.execute('SELECT * FROM trusted_quotes WHERE venue=? AND quote_id=?',(venue,quote_id)).fetchone()
        if not row:
            raise ReservationError('UNKNOWN_QUOTE')
        if row['session_id'] != session:
            raise ReservationError('QUOTE_SESSION_MISMATCH')
        return row

    def accept_quote(self, venue, session, quote_id, expected_total_minor):
        self._venue(venue)
        self._session(session)
        self._quote_id(quote_id)
        if type(expected_total_minor) is not int or not 0 <= expected_total_minor <= _MAX:
            raise ReservationError('INVALID_EXPECTED_TOTAL')
        now = self._time()
        with self._transaction() as db:
            row = self._load(db,venue,session,quote_id)
            if row['expires_ms'] <= now:
                raise ReservationError('QUOTE_EXPIRED')
            if row['total_minor'] != expected_total_minor:
                raise ReservationError('QUOTE_TOTAL_CONFLICT')
            self._fresh(db,row)
            db.execute("UPDATE trusted_quotes SET status='accepted' WHERE venue=? AND quote_id=?",(venue,quote_id))
            return self._quote_record(self._load(db,venue,session,quote_id))

    def reserve_accepted_quote(self, venue, session, quote_id, key):
        """Atomic quote+recipe+stock check. No client-provided prices or demands."""
        self._venue(venue)
        self._session(session)
        self._quote_id(quote_id)
        self._key(key)
        now = self._time()
        with self._transaction() as db:
            self._expire(db,venue,now)
            row = self._load(db,venue,session,quote_id)
            if row['reservation_key'] is not None:
                if row['reservation_key'] != key:
                    raise ReservationError('QUOTE_ALREADY_RESERVED')
                return self._record(self._get(db,venue,key))
            if row['status'] != 'accepted':
                raise ReservationError('QUOTE_NOT_ACCEPTED')
            if row['expires_ms'] <= now:
                raise ReservationError('QUOTE_EXPIRED')
            self._fresh(db,row)
            if self._get(db,venue,key):
                raise ReservationError('IDEMPOTENCY_CONFLICT')
            demands = json.loads(row['demands'])
            available = self._available(db,venue)
            missing = [{'ingredientId':i,'required':q,'available':max(0,available.get(i,0))}
                       for i,q in demands.items() if q > available.get(i,0)]
            if missing:
                raise ReservationError('INSUFFICIENT_RESERVABLE_STOCK',missing)
            db.execute('INSERT INTO reservations VALUES(?,?,?,?,?,?,NULL)',
                (venue,key,_json(demands),'held',now,row['expires_ms']))
            db.execute('UPDATE trusted_quotes SET reservation_key=? WHERE venue=? AND quote_id=?',
                (key,venue,quote_id))
            return self._record(self._get(db,venue,key))
