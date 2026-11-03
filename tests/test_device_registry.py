"""Trusted-only demo device registry regression tests."""
import os
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from device_registry import DemoDeviceRegistry
from outlet_permissions import AccessDenied


class DeviceRegistryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = os.path.join(self.temp.name, 'demo.sqlite')
        self.devices = DemoDeviceRegistry(self.path)

    def test_persistent_venue_scoped_capability(self):
        token = self.devices.provision_trusted('blackstock', 'bar-ipad', 'bar')
        self.assertEqual(DemoDeviceRegistry(self.path).resolve_trusted('blackstock', token),
                         {'venueId': 'blackstock', 'deviceId': 'bar-ipad', 'outletId': 'bar'})
        with self.assertRaises(AccessDenied):
            self.devices.resolve_trusted('another-venue', token)
        with open(self.path, 'rb') as handle:
            self.assertNotIn(token.encode(), handle.read())

    def test_rotation_invalidates_old_token(self):
        old = self.devices.provision_trusted('blackstock', 'till-1', 'bar')
        new = self.devices.provision_trusted('blackstock', 'till-1', 'spuddy')
        with self.assertRaises(AccessDenied):
            self.devices.resolve_trusted('blackstock', old)
        self.assertEqual(self.devices.resolve_trusted('blackstock', new)['outletId'], 'spuddy')

    def test_revocation_and_venue_isolation(self):
        token = self.devices.provision_trusted('blackstock', 'till-1', 'bar')
        other = self.devices.provision_trusted('other', 'till-1', 'bar')
        self.devices.revoke_trusted('blackstock', 'till-1')
        with self.assertRaises(AccessDenied):
            self.devices.resolve_trusted('blackstock', token)
        self.assertEqual(self.devices.resolve_trusted('other', other)['deviceId'], 'till-1')

    def test_expiry(self):
        with patch('device_registry.time.time', return_value=100):
            token = self.devices.provision_trusted('blackstock', 'till-1', 'bar', 1)
        with patch('device_registry.time.time', return_value=101):
            with self.assertRaises(AccessDenied):
                self.devices.resolve_trusted('blackstock', token)

    def test_invalid_inputs(self):
        for ttl in (0, -1, 86401, True, 1.5):
            with self.assertRaises(ValueError):
                self.devices.provision_trusted('blackstock', 'till', 'bar', ttl)
        with self.assertRaises(ValueError):
            self.devices.provision_trusted('bad venue', 'till', 'bar')
        for args in (('blackstock', 'bad device', 'bar'),
                     ('blackstock', 'till', 'bad outlet'),
                     ('bad\tvenue', 'till', 'bar')):
            with self.assertRaises(ValueError):
                self.devices.provision_trusted(*args)
        with self.assertRaises(AccessDenied):
            self.devices.resolve_trusted('blackstock', 'not-a-token')


if __name__ == '__main__':
    unittest.main()
