"""Provisioned demo staff bearer capabilities; NOT human login or an HTTP service.

Only trusted provisioning code may issue capabilities. Tokens are never stored
in plaintext. A protected operation checks token, active staff membership and
outlet policy under the same SQLite writer transaction as its mutation.
"""
import hashlib
import secrets
import time
from outlet_permissions import AccessDenied, Principal, require_permission
from staff_directory import SQLiteStaffDirectory


class DemoStaffSessions:
    def __init__(self, path):
        self.directory = SQLiteStaffDirectory(path)
        with self.directory._connect() as db:
            db.execute('''CREATE TABLE IF NOT EXISTS demo_staff_sessions (
                digest TEXT PRIMARY KEY, venue TEXT NOT NULL, subject TEXT NOT NULL,
                expires_at INTEGER NOT NULL, revoked INTEGER NOT NULL DEFAULT 0
                CHECK(revoked IN (0,1)))''')

    @staticmethod
    def _digest(token):
        if not isinstance(token, str) or len(token) != 64:
            raise AccessDenied('INVALID_CREDENTIAL')
        try:
            bytes.fromhex(token)
        except ValueError as exc:
            raise AccessDenied('INVALID_CREDENTIAL') from exc
        return hashlib.sha256(token.encode('ascii')).hexdigest()

    def provision_trusted(self, venue, subject, ttl_seconds=900):
        """Trusted fixture ONLY: provisioning is not a login endpoint."""
        self.directory._valid(venue)
        self.directory._valid(subject)
        if type(ttl_seconds) is not int or not 1 <= ttl_seconds <= 3600:
            raise ValueError('INVALID_TTL')
        token = secrets.token_hex(32)
        with self.directory._connect() as db:
            db.execute('BEGIN IMMEDIATE')
            active = db.execute('SELECT 1 FROM staff_memberships WHERE venue=? AND subject=? AND active=1',
                                (venue, subject)).fetchone()
            if not active:
                raise AccessDenied('STAFF_NOT_ACTIVE')
            db.execute('INSERT INTO demo_staff_sessions VALUES(?,?,?,?,0)',
                       (self._digest(token), venue, subject, int(time.time()) + ttl_seconds))
        return token

    def revoke_trusted(self, token):
        """Trusted-only revocation; no public revocation API."""
        digest = self._digest(token)
        with self.directory._connect() as db:
            db.execute('BEGIN IMMEDIATE')
            db.execute('UPDATE demo_staff_sessions SET revoked=1 WHERE digest=?', (digest,))

    def execute(self, venue, token, operation, outlet, mutation):
        """Single-database atomic authorisation and trusted mutation.

        Never pass user-defined callbacks or perform network side effects here.
        """
        if not callable(mutation):
            raise TypeError('TRUSTED_MUTATION_REQUIRED')
        self.directory._valid(venue)
        digest = self._digest(token)
        with self.directory._connect() as db:
            db.execute('BEGIN IMMEDIATE')
            row = db.execute('''SELECT subject FROM demo_staff_sessions
                WHERE digest=? AND venue=? AND revoked=0 AND expires_at>?''',
                (digest, venue, int(time.time()))).fetchone()
            if not row:
                raise AccessDenied('CREDENTIAL_DENIED')
            subject = row[0]
            membership = db.execute('''SELECT role FROM staff_memberships
                WHERE venue=? AND subject=? AND active=1''', (venue, subject)).fetchone()
            if not membership:
                raise AccessDenied('STAFF_NOT_ACTIVE')
            outlets = frozenset(r[0] for r in db.execute('''SELECT outlet FROM staff_outlets
                WHERE venue=? AND subject=?''', (venue, subject)))
            principal = Principal(subject, venue, membership[0], outlets)
            require_permission(principal, venue, operation, outlet)
            return mutation(db, principal)
