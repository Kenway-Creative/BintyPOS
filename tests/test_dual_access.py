"""Dual-capability read-only guard regressions."""
import os
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from dual_access import DemoDualAccess
from outlet_permissions import AccessDenied


class DualAccessTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.guard = DemoDualAccess(os.path.join(self.tmp.name, 'test.sqlite'))
        self.guard.sessions.directory.enrol_trusted('blackstock', 'alice', 'outlet_manager', ('spuddy',))
        self.staff = self.guard.sessions.provision_trusted('blackstock', 'alice')
        self.device = self.guard.devices.provision_trusted('blackstock', 'till1', 'spuddy')

    def read(self, venue='blackstock', outlet='spuddy', staff=None, device=None):
        return self.guard.read_trusted(venue, outlet, staff or self.staff, device or self.device)

    def test_authorised_and_persistent(self):
        self.assertEqual(self.read()['deviceId'], 'till1')
        reopened = DemoDualAccess(self.guard.sessions.directory.path)
        self.assertEqual(reopened.read_trusted('blackstock', 'spuddy', self.staff, self.device)['subject'], 'alice')

    def test_cross_venue_outlet_and_forged_credentials(self):
        for venue, outlet, staff, device in (
            ('other', 'spuddy', self.staff, self.device),
            ('blackstock', 'bar', self.staff, self.device),
            ('blackstock', 'spuddy', '0' * 64, self.device),
            ('blackstock', 'spuddy', self.staff, '0' * 64)):
            with self.subTest(venue=venue, outlet=outlet):
                with self.assertRaises(AccessDenied):
                    self.read(venue, outlet, staff, device)

    def test_rotation_and_revocation(self):
        old = self.device
        self.device = self.guard.devices.provision_trusted('blackstock', 'till1', 'spuddy')
        with self.assertRaises(AccessDenied):
            self.read(device=old)
        self.assertTrue(self.read()['allowed'])
        self.guard.devices.revoke_trusted('blackstock', 'till1')
        with self.assertRaises(AccessDenied):
            self.read()

    def test_staff_revocation_and_role_change(self):
        self.guard.sessions.directory.enrol_trusted('blackstock', 'alice', 'staff', ('spuddy',))
        self.assertTrue(self.read()['allowed'])
        self.guard.sessions.directory.revoke_trusted('blackstock', 'alice')
        with self.assertRaises(AccessDenied):
            self.read()

    def test_device_expiry(self):
        with patch('device_registry.time.time', return_value=100):
            self.device = self.guard.devices.provision_trusted('blackstock', 'till1', 'spuddy', 1)
        with patch('dual_access.time.time', return_value=101):
            with self.assertRaises(AccessDenied):
                self.read()


if __name__ == '__main__':
    unittest.main()
