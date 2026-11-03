"""Durable trusted-only staff membership resolver; NOT human authentication.

Only a trusted bootstrap service may enrol, revoke or resolve subjects. Never
accept subject IDs directly from a browser or expose these methods as HTTP.
"""
import sqlite3
from outlet_permissions import Principal, AccessDenied, require_permission

class SQLiteStaffDirectory:
    def __init__(self, path):
        self.path = path
        with self._connect() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS staff_memberships (
                venue TEXT NOT NULL, subject TEXT NOT NULL, role TEXT NOT NULL
                CHECK(role IN ('venue_admin','outlet_manager','staff')),
                active INTEGER NOT NULL DEFAULT 1 CHECK(active IN (0,1)),
                PRIMARY KEY(venue, subject))""")
            db.execute("""CREATE TABLE IF NOT EXISTS staff_outlets (
                venue TEXT NOT NULL, subject TEXT NOT NULL, outlet TEXT NOT NULL,
                PRIMARY KEY(venue,subject,outlet),
                FOREIGN KEY(venue,subject) REFERENCES staff_memberships(venue,subject)
            )""")

    def _connect(self):
        db = sqlite3.connect(self.path, timeout=10)
        db.execute('PRAGMA foreign_keys=ON')
        return db

    @staticmethod
    def _valid(value):
        if not isinstance(value, str) or not value.strip() or len(value) > 128:
            raise ValueError('INVALID_IDENTIFIER')
        return value

    def enrol_trusted(self, venue, subject, role, outlets=()):
        """Trusted bootstrap only; replace membership atomically, never merge stale grants."""
        self._valid(venue)
        self._valid(subject)
        scopes = tuple(outlets)
        if len(scopes) != len(set(scopes)):
            raise ValueError('DUPLICATE_OUTLET')
        for outlet in scopes:
            self._valid(outlet)
        principal = Principal(subject, venue, role, frozenset(scopes))
        with self._connect() as db:
            db.execute('BEGIN IMMEDIATE')
            db.execute("""INSERT INTO staff_memberships(venue,subject,role,active)
                VALUES(?,?,?,1) ON CONFLICT(venue,subject)
                DO UPDATE SET role=excluded.role, active=1""", (venue, subject, role))
            db.execute('DELETE FROM staff_outlets WHERE venue=? AND subject=?', (venue, subject))
            db.executemany('INSERT INTO staff_outlets VALUES(?,?,?)',
                           [(venue, subject, outlet) for outlet in scopes])
        return principal

    def revoke_trusted(self, venue, subject):
        self._valid(venue)
        self._valid(subject)
        with self._connect() as db:
            db.execute('BEGIN IMMEDIATE')
            db.execute('UPDATE staff_memberships SET active=0 WHERE venue=? AND subject=?',
                       (venue, subject))

    def resolve_trusted(self, venue, subject):
        """Caller must already have verified the human/device independently."""
        self._valid(venue)
        self._valid(subject)
        with self._connect() as db:
            db.execute('BEGIN')
            row = db.execute('SELECT role FROM staff_memberships WHERE venue=? AND subject=? AND active=1',
                             (venue, subject)).fetchone()
            if row is None:
                raise AccessDenied('STAFF_NOT_ACTIVE')
            outlets = frozenset(r[0] for r in db.execute(
                'SELECT outlet FROM staff_outlets WHERE venue=? AND subject=?',
                (venue, subject)))
            return Principal(subject, venue, row[0], outlets)

    def require_trusted(self, venue, subject, operation, outlet=None):
        """Resolve and authorise under a single SQLite read transaction.

        This is a read-only policy check, NOT a transactional guard around
        an external mutation. Protected writes must recheck inside their
        own writer transaction on the same database.
        """
        principal = self.resolve_trusted(venue, subject)
        return require_permission(principal, venue, operation, outlet)
