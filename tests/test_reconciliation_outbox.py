"""Mock reconciliation queue: durable, idempotent, never infers payment success."""
import os
import sys
import tempfile
import unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from reconciliation_outbox import MockReconciliationOutbox
from order_lifecycle import MockPaymentAdapter

class OutboxTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.temp.name, 'db.sqlite')
        self.clock = [100000]
        self.api = MockReconciliationOutbox(self.path, now=lambda: self.clock[0],
                                             payment=MockPaymentAdapter(capture=False))
        self.api.bootstrap_stock('venue', {'beer': 3})
        self.api.publish_product('venue', 'pint', 'bar', 500, {'beer': 1})

    def tearDown(self):
        self.temp.cleanup()

    def test_durable_idempotent_queue_and_no_stock_mutation(self):
        q = self.api.create_quote('venue', 'session', [{'productId':'pint','quantity':1}])
        self.api.accept_quote('venue', 'session', q['quoteId'], 500)
        order = self.api.create_order('venue', 'session', q['quoteId'], 'key')
        self.api.authorise_mock('venue', 'session', order['orderId'])
        self.api.complete_mock('venue', 'session', order['orderId'])
        first = self.api.snapshot_pending('venue')
        self.assertEqual(len(first), 1)
        self.assertEqual(first[0]['reason'], 'MOCK_CAPTURE_UNKNOWN')
        self.assertEqual(self.api.snapshot_pending('venue'), first)
        self.clock[0] += 10
        reopened = MockReconciliationOutbox(self.path, now=lambda: self.clock[0])
        later = reopened.snapshot_pending('venue')
        self.assertEqual(later[0]['firstSeenAt'], first[0]['firstSeenAt'])
        self.assertEqual(later[0]['lastSeenAt'], self.clock[0])
        self.assertEqual(reopened.available('venue')['beer'], 2)
        self.assertEqual(reopened.status_order('venue', 'session', order['orderId'])['status'], 'needs_reconciliation')
        self.assertEqual(reopened.snapshot_pending('other'), [])

    def test_empty_queue_and_invalid_venue(self):
        self.assertEqual(self.api.snapshot_pending('venue'), [])
        with self.assertRaises(ValueError):
            self.api.snapshot_pending('../other')

if __name__ == '__main__':
    unittest.main()
