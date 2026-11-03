"""Trusted fixture device enrolment. NOT device attestation, login or HTTP pairing."""
import hashlib
import secrets
import time
from staff_directory import SQLiteStaffDirectory
from outlet_permissions import AccessDenied


class DemoDeviceRegistry:
    """Opaque device capability with hashed storage and revocation.

    Provisioning requires an already-trusted operator process. Device credentials
    are never staff credentials and cannot authorise staff or checkout operations.
    """
    def __init__(self, path):
        self.directory = SQLiteStaffDirectory(path)
        with self.directory._connect() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS demo_devices (
                digest TEXT PRIMARY KEY, venue TEXT NOT NULL, device_id TEXT NOT NULL,
                outlet TEXT NOT NULL, expires_at INTEGER NOT NULL,
                revoked INTEGER NOT NULL DEFAULT 0 CHECK(revoked IN (0,1)),
                UNIQUE(venue, device_id))""")

    @staticmethod
    def _digest(token):
        if not isinstance(token, str) or len(token) != 64:
            raise AccessDenied('INVALID_DEVICE_CREDENTIAL')
        try:
            bytes.fromhex(token)
        except ValueError as exc:
            raise AccessDenied('INVALID_DEVICE_CREDENTIAL') from exc
        return hashlib.sha256(token.encode('ascii')).hexdigest()

    @staticmethod
    def _valid_device_identifier(value):
        # Device/venue/outlet IDs are stable machine identifiers, not display names.
        # Disallow embedded whitespace while preserving existing namespace punctuation.
        SQLiteStaffDirectory._valid(value)
        if any(character.isspace() for character in value):
            raise ValueError('INVALID_DEVICE_IDENTIFIER')
        return value

    def provision_trusted(self, venue, device_id, outlet, ttl_seconds=3600):
        for value in (venue, device_id, outlet):
            self._valid_device_identifier(value)
        if type(ttl_seconds) is not int or not 1 <= ttl_seconds <= 86400:
            raise ValueError('INVALID_DEVICE_TTL')
        token = secrets.token_hex(32)
        with self.directory._connect() as db:
            db.execute('BEGIN IMMEDIATE')
            # A replacement rotates the credential and invalidates the old one.
            db.execute('DELETE FROM demo_devices WHERE venue=? AND device_id=?',
                       (venue, device_id))
            db.execute('INSERT INTO demo_devices VALUES(?,?,?,?,?,0)',
                       (self._digest(token), venue, device_id, outlet,
                        int(time.time()) + ttl_seconds))
        return token

    def resolve_trusted(self, venue, token):
        self.directory._valid(venue)
        digest = self._digest(token)
        with self.directory._connect() as db:
            row = db.execute("""SELECT device_id, outlet FROM demo_devices
                WHERE digest=? AND venue=? AND revoked=0 AND expires_at>?""",
                (digest, venue, int(time.time()))).fetchone()
        if row is None:
            raise AccessDenied('DEVICE_DENIED')
        return {'venueId': venue, 'deviceId': row[0], 'outletId': row[1]}

    def revoke_trusted(self, venue, device_id):
        self.directory._valid(venue)
        self.directory._valid(device_id)
        with self.directory._connect() as db:
            db.execute('BEGIN IMMEDIATE')
            db.execute('UPDATE demo_devices SET revoked=1 WHERE venue=? AND device_id=?',
                       (venue, device_id))
