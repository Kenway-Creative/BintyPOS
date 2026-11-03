"""Trusted mock-only reconciliation audit decisions."""
import os
import sys
import tempfile
import unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from reconciliation_outbox import MockReconciliationOutbox
from order_lifecycle import MockPaymentAdapter


class AuditTests(unittest.TestCase):
    def test_durable_append_only_review_and_idempotency(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, 'db.sqlite')
            api = MockReconciliationOutbox(path, now=lambda: 123456, payment=MockPaymentAdapter(capture=False))
            api.bootstrap_stock('venue', {'beer': 2})
            api.publish_product('venue', 'pint', 'bar', 500, {'beer': 1})
            quote = api.create_quote('venue', 'session', [{'productId': 'pint', 'quantity': 1}])
            api.accept_quote('venue', 'session', quote['quoteId'], 500)
            order = api.create_order('venue', 'session', quote['quoteId'], 'reserve-key')
            api.authorise_mock('venue', 'session', order['orderId'])
            api.complete_mock('venue', 'session', order['orderId'])
            api.snapshot_pending('venue')
            first = api.record_manual_decision('venue', order['orderId'], 'demo-manager', 'investigate', 'Mock capture unknown', 'review-1')
            self.assertEqual(len(first), 1)
            self.assertEqual(api.record_manual_decision('venue', order['orderId'], 'demo-manager', 'investigate', 'Mock capture unknown', 'review-1'), first)
            with self.assertRaises(ValueError):
                api.record_manual_decision('venue', order['orderId'], 'demo-manager', 'acknowledge', 'Changed', 'review-1')
            reopened = MockReconciliationOutbox(path)
            self.assertEqual(reopened.list_manual_decisions('venue', order['orderId']), first)
            self.assertEqual(reopened.list_manual_decisions('other', order['orderId']), [])
            self.assertEqual(reopened.status_order('venue', 'session', order['orderId'])['status'], 'needs_reconciliation')
            self.assertEqual(reopened.available('venue')['beer'], 1)

    def test_reject_unknown_entry_and_invalid_decision(self):
        with tempfile.TemporaryDirectory() as directory:
            api = MockReconciliationOutbox(os.path.join(directory, 'db.sqlite'))
            with self.assertRaises(ValueError):
                api.record_manual_decision('venue', 'missing', 'actor', 'investigate', 'note', 'key')
            with self.assertRaises(ValueError):
                api.record_manual_decision('venue', 'missing', 'actor', 'resolved', 'note', 'key')
