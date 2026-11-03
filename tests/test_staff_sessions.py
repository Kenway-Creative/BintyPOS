"""Regression tests for provisioned demo staff sessions."""
import os
import sqlite3
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from staff_sessions import DemoStaffSessions
from outlet_permissions import AccessDenied


class SessionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.temp.name, 'test.db')
        self.api = DemoStaffSessions(self.path)
        self.api.directory.enrol_trusted('venue', 'alice', 'outlet_manager', ('spuddy',))
        with sqlite3.connect(self.path) as db:
            db.execute('CREATE TABLE writes (subject TEXT)')
        self.token = self.api.provision_trusted('venue', 'alice')

    def tearDown(self):
        self.temp.cleanup()

    def write(self, db, principal):
        db.execute('INSERT INTO writes VALUES(?)', (principal.subject,))
        return principal.subject

    def count(self):
        with sqlite3.connect(self.path) as db:
            return db.execute('SELECT COUNT(*) FROM writes').fetchone()[0]

    def test_valid_and_hashed_at_rest(self):
        self.assertEqual(self.api.execute('venue', self.token, 'stock.count.submit', 'spuddy', self.write), 'alice')
        with sqlite3.connect(self.path) as db:
            digest, = db.execute('SELECT digest FROM demo_staff_sessions').fetchone()
        self.assertNotEqual(digest, self.token)
        self.assertEqual(self.count(), 1)

    def test_cross_venue_and_outlet(self):
        for venue, outlet in [('other', 'spuddy'), ('venue', 'bar')]:
            with self.assertRaises(AccessDenied):
                self.api.execute(venue, self.token, 'stock.count.submit', outlet, self.write)
        self.assertEqual(self.count(), 0)

    def test_revocation_and_membership_revocation(self):
        self.api.revoke_trusted(self.token)
        with self.assertRaises(AccessDenied):
            self.api.execute('venue', self.token, 'stock.count.submit', 'spuddy', self.write)
        fresh = self.api.provision_trusted('venue', 'alice')
        self.api.directory.revoke_trusted('venue', 'alice')
        with self.assertRaises(AccessDenied):
            self.api.execute('venue', fresh, 'stock.count.submit', 'spuddy', self.write)

    def test_role_change_applies_to_existing_token(self):
        self.api.directory.enrol_trusted('venue', 'alice', 'staff', ('spuddy',))
        with self.assertRaises(AccessDenied):
            self.api.execute('venue', self.token, 'stock.count.submit', 'spuddy', self.write)
        self.assertEqual(self.api.execute('venue', self.token, 'stock.count.read', 'spuddy', self.write), 'alice')

    def test_expiry_and_bad_token(self):
        with patch('staff_sessions.time.time', return_value=9999999999):
            with self.assertRaises(AccessDenied):
                self.api.execute('venue', self.token, 'stock.count.submit', 'spuddy', self.write)
        for token in ('invalid', 'z'*64, None):
            with self.assertRaises(AccessDenied):
                self.api.execute('venue', token, 'stock.count.submit', 'spuddy', self.write)

    def test_failure_rolls_back(self):
        def broken(db, principal):
            self.write(db, principal)
            raise RuntimeError('fail')
        with self.assertRaises(RuntimeError):
            self.api.execute('venue', self.token, 'stock.count.submit', 'spuddy', broken)
        self.assertEqual(self.count(), 0)

    def test_persistent_restart_and_inactive_provision_denied(self):
        reopened = DemoStaffSessions(self.path)
        self.assertEqual(reopened.execute('venue', self.token, 'stock.count.submit', 'spuddy', self.write), 'alice')
        reopened.directory.revoke_trusted('venue', 'alice')
        with self.assertRaises(AccessDenied):
            reopened.provision_trusted('venue', 'alice')

    def test_ttl_validation(self):
        for ttl in (0, 3601, True, '900'):
            with self.assertRaises(ValueError):
                self.api.provision_trusted('venue', 'alice', ttl)


if __name__ == '__main__':
    unittest.main()
