"""Durable staff fixture tests; subject is trusted, not browser-authenticated."""
import os
import sys
import tempfile
import unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from staff_directory import SQLiteStaffDirectory
from outlet_permissions import AccessDenied

class DirectoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.temp.name, 'staff.db')
        self.directory = SQLiteStaffDirectory(self.path)

    def tearDown(self):
        self.temp.cleanup()

    def test_restart_and_scope(self):
        self.directory.enrol_trusted('blackstock', 'mike', 'outlet_manager', ('spuddy',))
        reopened = SQLiteStaffDirectory(self.path)
        self.assertTrue(reopened.require_trusted('blackstock', 'mike', 'stock.count.submit', 'spuddy'))
        with self.assertRaises(AccessDenied):
            reopened.require_trusted('blackstock', 'mike', 'stock.count.submit', 'bar')

    def test_venue_isolation(self):
        self.directory.enrol_trusted('blackstock', 'mike', 'venue_admin')
        with self.assertRaises(AccessDenied):
            self.directory.require_trusted('other', 'mike', 'catalogue.approve')

    def test_revoke_persists(self):
        self.directory.enrol_trusted('blackstock', 'mike', 'venue_admin')
        self.directory.revoke_trusted('blackstock', 'mike')
        with self.assertRaises(AccessDenied):
            SQLiteStaffDirectory(self.path).resolve_trusted('blackstock', 'mike')

    def test_reenrol_replaces_old_scopes(self):
        self.directory.enrol_trusted('blackstock', 'mike', 'outlet_manager', ('spuddy',))
        self.directory.enrol_trusted('blackstock', 'mike', 'staff', ('bar',))
        with self.assertRaises(AccessDenied):
            self.directory.require_trusted('blackstock', 'mike', 'stock.count.submit', 'spuddy')
        self.assertTrue(self.directory.require_trusted('blackstock', 'mike', 'stock.count.read', 'bar'))

    def test_unknown_and_invalid(self):
        with self.assertRaises(AccessDenied):
            self.directory.resolve_trusted('blackstock', 'missing')
        with self.assertRaises(ValueError):
            self.directory.enrol_trusted('blackstock', 'x', 'root')
        with self.assertRaises(ValueError):
            self.directory.enrol_trusted('blackstock', 'x', 'staff', ('bar', 'bar'))

if __name__ == '__main__':
    unittest.main()
