"""Trusted fixture back-office transaction regression tests."""
import os
import sys
import sqlite3
import tempfile
import threading
import unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from guarded_staff_operations import GuardedStaffOperations
from outlet_permissions import AccessDenied


class GuardTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.temp.name, 'guard.db')
        self.guard = GuardedStaffOperations(self.path)
        self.guard.directory.enrol_trusted('blackstock', 'manager', 'outlet_manager', ('spuddy',))
        with sqlite3.connect(self.path) as db:
            db.execute('CREATE TABLE changes (outlet TEXT, value TEXT)')

    def tearDown(self):
        self.temp.cleanup()

    def write(self, db, principal):
        db.execute('INSERT INTO changes VALUES (?,?)', ('spuddy', principal.subject))
        return principal.subject

    def count(self):
        with sqlite3.connect(self.path) as db:
            return db.execute('SELECT COUNT(*) FROM changes').fetchone()[0]

    def test_authorised_write(self):
        self.assertEqual(self.guard.execute_trusted('blackstock', 'manager', 'stock.count.submit', 'spuddy', self.write), 'manager')
        self.assertEqual(self.count(), 1)

    def test_cross_outlet_denied(self):
        with self.assertRaises(AccessDenied):
            self.guard.execute_trusted('blackstock', 'manager', 'stock.count.submit', 'bar', self.write)
        self.assertEqual(self.count(), 0)

    def test_revoke_denies_write(self):
        self.guard.directory.revoke_trusted('blackstock', 'manager')
        with self.assertRaises(AccessDenied):
            self.guard.execute_trusted('blackstock', 'manager', 'stock.count.submit', 'spuddy', self.write)
        self.assertEqual(self.count(), 0)

    def test_mutation_failure_rolls_back(self):
        def fail(db, principal):
            self.write(db, principal)
            raise RuntimeError('fail')
        with self.assertRaises(RuntimeError):
            self.guard.execute_trusted('blackstock', 'manager', 'stock.count.submit', 'spuddy', fail)
        self.assertEqual(self.count(), 0)

    def test_revocation_waits_for_write(self):
        entered, release = threading.Event(), threading.Event()
        errors = []
        def slow(db, principal):
            self.write(db, principal)
            entered.set()
            if not release.wait(5):
                raise TimeoutError('test wait')
        def writer():
            try:
                self.guard.execute_trusted('blackstock', 'manager', 'stock.count.submit', 'spuddy', slow)
            except Exception as exc:
                errors.append(exc)
        t = threading.Thread(target=writer)
        t.start()
        self.assertTrue(entered.wait(5))
        revoker = threading.Thread(target=lambda: self.guard.directory.revoke_trusted('blackstock', 'manager'))
        revoker.start()
        self.assertTrue(revoker.is_alive())
        release.set()
        t.join(5)
        revoker.join(5)
        self.assertFalse(errors)
        self.assertEqual(self.count(), 1)
        with self.assertRaises(AccessDenied):
            self.guard.execute_trusted('blackstock', 'manager', 'stock.count.submit', 'spuddy', self.write)


if __name__ == '__main__':
    unittest.main()
