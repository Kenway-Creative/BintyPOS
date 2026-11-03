"""Recovery is mock-only: inspect safely, never invent a payment result."""
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from order_recovery import MockOrderRecovery
from order_lifecycle import MockPaymentAdapter


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.clock = [100000]
        self.path = os.path.join(self.tmp.name, 'orders.sqlite')
        self.api = MockOrderRecovery(self.path, now=lambda: self.clock[0])
        self.api.bootstrap_stock('venue', {'beer': 5})
        self.api.publish_product('venue', 'pint', 'bar', 500, {'beer': 1})

    def tearDown(self):
        self.tmp.cleanup()

    def quote(self):
        q = self.api.create_quote('venue', 'session', [{'productId': 'pint', 'quantity': 1}])
        self.api.accept_quote('venue', 'session', q['quoteId'], 500)
        return q['quoteId']

    def test_orphan_hold_visible_and_expiry_idempotent_across_restart(self):
        q = self.quote()
        self.api.reserve_accepted_quote('venue', 'session', q, 'orphan')
        self.assertEqual(self.api.available('venue')['beer'], 4)
        first = self.api.inspect_recovery('venue')
        self.assertEqual(first['orphanHolds'][0]['reservationStatus'], 'held')
        self.assertEqual(self.api.inspect_recovery('venue')['orphanHolds'], first['orphanHolds'])
        self.clock[0] += 120001
        restarted = MockOrderRecovery(self.path, now=lambda: self.clock[0])
        self.assertEqual(restarted.inspect_recovery('venue')['orphanHolds'][0]['reservationStatus'], 'expired')
        self.assertEqual(restarted.available('venue')['beer'], 5)

    def test_linked_order_not_orphan_and_expiry(self):
        q = self.quote()
        order = self.api.create_order('venue', 'session', q, 'linked')
        self.assertEqual(self.api.inspect_recovery('venue')['orphanHolds'], [])
        self.clock[0] += 120001
        self.api.inspect_recovery('venue')
        self.assertEqual(self.api.status_order('venue', 'session', order['orderId'])['status'], 'expired')

    def test_ambiguous_capture_never_auto_confirmed_or_released(self):
        self.api.payment = MockPaymentAdapter(capture=False)
        q = self.quote()
        order = self.api.create_order('venue', 'session', q, 'capture-unknown')
        self.api.authorise_mock('venue', 'session', order['orderId'])
        self.api.complete_mock('venue', 'session', order['orderId'])
        report = self.api.inspect_recovery('venue')
        self.assertEqual(report['needsManualReconciliation'][0]['reason'], 'MOCK_CAPTURE_UNKNOWN')
        self.assertEqual(self.api.status_order('venue', 'session', order['orderId'])['status'], 'needs_reconciliation')
        self.assertEqual(self.api.available('venue')['beer'], 4)

    def test_venue_isolation(self):
        self.api.bootstrap_stock('other', {'beer': 2})
        self.assertEqual(self.api.inspect_recovery('other')['orphanHolds'], [])
        self.assertEqual(self.api.inspect_recovery('other')['needsManualReconciliation'], [])


if __name__ == '__main__':
    unittest.main()
