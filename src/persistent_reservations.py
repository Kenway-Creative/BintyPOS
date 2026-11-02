"""BintyPOS 0.2.9 SQLite transaction proof-of-concept. NOT a network/API service.

Only trusted server code may call this adapter. Demand is passed directly for tests;
production must derive it from a server-authorised, accepted quote and recipes.
"""
from contextlib import contextmanager
import json
import re
import sqlite3
import time

_ID = re.compile(r"[a-z0-9][a-z0-9-]*\Z")
_KEY = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,127}\Z")
_MAX = 2**53 - 1


class ReservationError(ValueError):
    def __init__(self, code, shortages=None):
        super().__init__(code)
        self.code = code
        self.shortages = shortages or []


def _valid_id(value):
    return isinstance(value, str) and bool(_ID.fullmatch(value))


def _demands(value):
    if not isinstance(value, dict):
        raise ReservationError("INVALID_RESERVATION_DEMAND")
    for ingredient, qty in value.items():
        if not _valid_id(ingredient) or type(qty) is not int or not 0 < qty <= _MAX:
            raise ReservationError("INVALID_RESERVATION_DEMAND")
    return dict(sorted(value.items()))


class SQLiteReservations:
    """Single-file SQLite store: BEGIN IMMEDIATE serialises competing writers.

    One instance can be used by several threads; each operation opens a separate
    connection. Multiple processes may share the same on-disk database.
    """

    def __init__(self, path, now=None):
        if not isinstance(path, str) or not path or path == ":memory:":
            raise ValueError("A real SQLite file path is required")
        self.path = path
        self.now = now or (lambda: int(time.time() * 1000))
        with self._transaction() as db:
            db.execute("CREATE TABLE IF NOT EXISTS stock (venue TEXT NOT NULL, ingredient TEXT NOT NULL, qty INTEGER NOT NULL CHECK(qty >= 0), PRIMARY KEY(venue,ingredient))")
            db.execute("CREATE TABLE IF NOT EXISTS reservations (venue TEXT NOT NULL, key TEXT NOT NULL, demands TEXT NOT NULL, status TEXT NOT NULL CHECK(status IN ('held','expired','released','committed','conflicted')), created_ms INTEGER NOT NULL, expires_ms INTEGER NOT NULL, committed_ms INTEGER, PRIMARY KEY(venue,key))")
            db.execute("CREATE TABLE IF NOT EXISTS movements (venue TEXT NOT NULL, key TEXT NOT NULL, ingredient TEXT NOT NULL, qty INTEGER NOT NULL CHECK(qty > 0), PRIMARY KEY(venue,key,ingredient), FOREIGN KEY(venue,key) REFERENCES reservations(venue,key))")

    @contextmanager
    def _transaction(self):
        db = sqlite3.connect(self.path, timeout=10, isolation_level=None)
        db.row_factory = sqlite3.Row
        try:
            db.execute("PRAGMA busy_timeout=10000")
            db.execute("PRAGMA foreign_keys=ON")
            db.execute("BEGIN IMMEDIATE")
            try:
                yield db
            except BaseException:
                db.rollback()
                raise
            else:
                db.commit()
        finally:
            db.close()

    def _time(self):
        value = self.now()
        if type(value) is not int or not 0 <= value <= _MAX:
            raise ReservationError("INVALID_RESERVATION_CLOCK")
        return value

    @staticmethod
    def _venue(venue):
        if not _valid_id(venue):
            raise ReservationError("INVALID_VENUE_ID")

    @staticmethod
    def _key(key):
        if not isinstance(key, str) or not _KEY.fullmatch(key):
            raise ReservationError("INVALID_IDEMPOTENCY_KEY")

    @staticmethod
    def _record(row):
        if row is None:
            return None
        return {"venue": row["venue"], "key": row["key"],
                "demands": json.loads(row["demands"]), "status": row["status"],
                "createdAt": row["created_ms"], "expiresAt": row["expires_ms"],
                "committedAt": row["committed_ms"]}

    @staticmethod
    def _get(db, venue, key):
        return db.execute("SELECT * FROM reservations WHERE venue=? AND key=?", (venue, key)).fetchone()

    @staticmethod
    def _expire(db, venue, now):
        db.execute("UPDATE reservations SET status='expired' WHERE venue=? AND status='held' AND expires_ms<=?", (venue, now))

    @staticmethod
    def _available(db, venue):
        amounts = {r["ingredient"]: r["qty"] for r in db.execute("SELECT ingredient,qty FROM stock WHERE venue=?", (venue,))}
        for row in db.execute("SELECT demands FROM reservations WHERE venue=? AND status='held'", (venue,)):
            for ingredient, qty in json.loads(row["demands"]).items():
                amounts[ingredient] = amounts.get(ingredient, 0) - qty
        return amounts

    def bootstrap_stock(self, venue, amounts):
        """Test fixture ONLY. Insert missing rows; never restock or overwrite counts."""
        self._venue(venue)
        if not isinstance(amounts, dict) or any(not _valid_id(k) or type(v) is not int or not 0 <= v <= _MAX for k, v in amounts.items()):
            raise ReservationError("INVALID_RESERVATION_STOCK")
        with self._transaction() as db:
            for ingredient, qty in amounts.items():
                db.execute("INSERT OR IGNORE INTO stock VALUES(?,?,?)", (venue, ingredient, qty))

    def available(self, venue):
        self._venue(venue)
        now = self._time()
        with self._transaction() as db:
            self._expire(db, venue, now)
            return self._available(db, venue)

    def reserve(self, venue, key, demands, ttl_ms=120000):
        self._venue(venue)
        self._key(key)
        demands = _demands(demands)
        if type(ttl_ms) is not int or not 1000 <= ttl_ms <= 900000:
            raise ReservationError("INVALID_RESERVATION_TTL")
        now = self._time()
        if now + ttl_ms > _MAX:
            raise ReservationError("INVALID_RESERVATION_CLOCK")
        encoded = json.dumps(demands, sort_keys=True, separators=(",", ":"))
        with self._transaction() as db:
            self._expire(db, venue, now)
            old = self._get(db, venue, key)
            if old:
                if old["demands"] != encoded:
                    raise ReservationError("IDEMPOTENCY_CONFLICT")
                return self._record(old)
            available = self._available(db, venue)
            missing = [{"ingredientId": i, "required": q, "available": max(0, available.get(i, 0))}
                       for i, q in demands.items() if q > available.get(i, 0)]
            if missing:
                raise ReservationError("INSUFFICIENT_RESERVABLE_STOCK", missing)
            db.execute("INSERT INTO reservations VALUES(?,?,?,?,?,?,NULL)", (venue, key, encoded, "held", now, now + ttl_ms))
            return self._record(self._get(db, venue, key))

    def status(self, venue, key):
        self._venue(venue)
        self._key(key)
        now = self._time()
        with self._transaction() as db:
            self._expire(db, venue, now)
            return self._record(self._get(db, venue, key))

    def release(self, venue, key):
        self._venue(venue)
        self._key(key)
        now = self._time()
        with self._transaction() as db:
            self._expire(db, venue, now)
            old = self._get(db, venue, key)
            if not old:
                raise ReservationError("UNKNOWN_RESERVATION")
            if old["status"] == "committed":
                raise ReservationError("RESERVATION_ALREADY_COMMITTED")
            if old["status"] == "held":
                db.execute("UPDATE reservations SET status='released' WHERE venue=? AND key=?", (venue, key))
            return self._record(self._get(db, venue, key))

    def commit(self, venue, key):
        """Trusted internal transition ONLY. No payment verification or order ledger."""
        self._venue(venue)
        self._key(key)
        now = self._time()
        conflict = None
        with self._transaction() as db:
            self._expire(db, venue, now)
            old = self._get(db, venue, key)
            if not old:
                raise ReservationError("UNKNOWN_RESERVATION")
            if old["status"] == "committed":
                return self._record(old)
            if old["status"] != "held":
                raise ReservationError("RESERVATION_NOT_ACTIVE")
            demands = json.loads(old["demands"])
            for ingredient, qty in demands.items():
                row = db.execute("SELECT qty FROM stock WHERE venue=? AND ingredient=?", (venue, ingredient)).fetchone()
                if not row or row["qty"] < qty:
                    conflict = "RESERVATION_STOCK_CONFLICT"
                    break
            if conflict:
                db.execute("UPDATE reservations SET status='conflicted' WHERE venue=? AND key=?", (venue, key))
            else:
                for ingredient, qty in demands.items():
                    result = db.execute("UPDATE stock SET qty=qty-? WHERE venue=? AND ingredient=? AND qty>=?", (qty, venue, ingredient, qty))
                    if result.rowcount != 1:
                        raise ReservationError("RESERVATION_STOCK_CONFLICT")
                    db.execute("INSERT INTO movements VALUES(?,?,?,?)", (venue, key, ingredient, qty))
                db.execute("UPDATE reservations SET status='committed',committed_ms=? WHERE venue=? AND key=?", (now, venue, key))
            record = self._record(self._get(db, venue, key))
        if conflict:
            raise ReservationError(conflict)
        return record

    def movements(self, venue, key):
        self._venue(venue)
        self._key(key)
        with self._transaction() as db:
            return [dict(r) for r in db.execute("SELECT ingredient,qty FROM movements WHERE venue=? AND key=? ORDER BY ingredient", (venue, key))]
