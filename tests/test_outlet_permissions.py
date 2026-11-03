"""Pure policy regression tests; does not assert real staff authentication."""
import os
import sys
import unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from outlet_permissions import Principal, AccessDenied, require_permission

class OutletPolicyTests(unittest.TestCase):
    def setUp(self):
        self.admin = Principal('admin', 'blackstock', 'venue_admin')
        self.manager = Principal('mike', 'blackstock', 'outlet_manager', frozenset({'spuddy'}))
        self.staff = Principal('bar1', 'blackstock', 'staff', frozenset({'bar'}))

    def denied(self, principal, venue, action, outlet=None):
        with self.assertRaises(AccessDenied):
            require_permission(principal, venue, action, outlet)

    def test_admin_venue_action(self):
        self.assertTrue(require_permission(self.admin, 'blackstock', 'catalogue.approve'))
    def test_manager_own_outlet(self):
        self.assertTrue(require_permission(self.manager, 'blackstock', 'outlet.offering.propose', 'spuddy'))
    def test_cross_outlet_denied(self):
        self.denied(self.manager, 'blackstock', 'outlet.offering.propose', 'bar')
    def test_admin_requires_explicit_outlet(self):
        self.denied(self.admin, 'blackstock', 'outlet.offering.propose')
    def test_manager_cannot_approve(self):
        self.denied(self.manager, 'blackstock', 'catalogue.approve')
    def test_staff_cannot_manage(self):
        self.denied(self.staff, 'blackstock', 'stock.count.submit', 'bar')
    def test_staff_read_own(self):
        self.assertTrue(require_permission(self.staff, 'blackstock', 'stock.count.read', 'bar'))
    def test_wrong_venue(self):
        self.denied(self.admin, 'other', 'catalogue.approve')
    def test_unknown_action(self):
        self.denied(self.admin, 'blackstock', 'payments.capture')
    def test_untrusted_dict(self):
        self.denied({'role': 'venue_admin'}, 'blackstock', 'catalogue.approve')
    def test_venue_action_rejects_outlet(self):
        self.denied(self.admin, 'blackstock', 'catalogue.approve', 'bar')
    def test_invalid_principal(self):
        with self.assertRaises(ValueError): Principal('', 'blackstock', 'venue_admin')
        with self.assertRaises(ValueError): Principal('x', 'blackstock', 'root')
        with self.assertRaises(ValueError): Principal('x', 'blackstock', 'staff', {'bar'})

if __name__ == '__main__':
    unittest.main()
