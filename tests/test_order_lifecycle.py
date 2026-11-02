"""Mock-only order state tests. Run python -m unittest discover -s tests -p 'test_*.py' -v."""
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from order_lifecycle import SQLiteMockOrders, MockPaymentAdapter
from persistent_reservations import ReservationError


class OrderLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmp.name, 'orders.sqlite')
        self.clock = [10000]
        self.store = SQLiteMockOrders(self.path, now=lambda: self.clock[0])
        self.store.bootstrap_stock('blackstock', {'corona': 8})
        self.store.publish_product('blackstock', 'beer', 'bar', 450, {'corona': 1})

    def tearDown(self):
        self.tmp.cleanup()

    def order(self, key='a', session='till-one'):
        quote = self.store.create_quote('blackstock', session, [{'productId': 'beer', 'quantity': 2}])
        self.store.accept_quote('blackstock', session, quote['quoteId'], quote['totalMinor'])
        return self.store.create_order('blackstock', session, quote['quoteId'], key)

    def fail(self, code, callback):
        with self.assertRaises(ReservationError) as error:
            callback()
        self.assertEqual(error.exception.code, code)

    def test_happy_path_and_idempotent_replay(self):
        order = self.order()
        self.assertEqual(order['status'], 'awaiting_payment')
        self.assertEqual(order['totalMinor'], 900)
        self.assertEqual(self.store.authorise_mock('blackstock', 'till-one', order['orderId'])['status'], 'authorised')
        self.assertEqual(self.store.complete_mock('blackstock', 'till-one', order['orderId'])['status'], 'confirmed')
        self.assertEqual(self.store.complete_mock('blackstock', 'till-one', order['orderId'])['status'], 'confirmed')
        self.assertEqual(self.store.available('blackstock')['corona'], 6)
        self.assertEqual(self.store.movements('blackstock', 'a'), [{'ingredient':'corona','qty':2}])

    def test_no_completion_before_authorisation(self):
        order = self.order()
        self.fail('ORDER_INVALID_TRANSITION', lambda: self.store.complete_mock('blackstock','till-one',order['orderId']))
        self.assertEqual(self.store.available('blackstock')['corona'], 6)

    def test_cancel_releases_without_consumption(self):
        order = self.order()
        self.assertEqual(self.store.cancel_mock('blackstock','till-one',order['orderId'])['status'],'released')
        self.assertEqual(self.store.cancel_mock('blackstock','till-one',order['orderId'])['status'],'released')
        self.assertEqual(self.store.available('blackstock')['corona'], 8)
        self.fail('ORDER_INVALID_TRANSITION', lambda:self.store.authorise_mock('blackstock','till-one',order['orderId']))

    def test_declined_mock_releases_hold(self):
        self.store.payment = MockPaymentAdapter(approve=False)
        order = self.order()
        self.assertEqual(self.store.authorise_mock('blackstock','till-one',order['orderId'])['status'],'failed')
        self.assertEqual(self.store.available('blackstock')['corona'],8)

    def test_expired_hold_cannot_authorise(self):
        order = self.order()
        self.clock[0] += 120000
        self.assertEqual(self.store.status_order('blackstock','till-one',order['orderId'])['status'],'expired')
        self.fail('ORDER_INVALID_TRANSITION', lambda:self.store.authorise_mock('blackstock','till-one',order['orderId']))

    def test_wrong_session_and_venue_rejected(self):
        order = self.order()
        self.fail('ORDER_SESSION_MISMATCH', lambda:self.store.authorise_mock('blackstock','till-two',order['orderId']))
        self.fail('UNKNOWN_ORDER', lambda:self.store.status_order('other','till-one',order['orderId']))

    def test_restart_preserves_order(self):
        order = self.order()
        other = SQLiteMockOrders(self.path, now=lambda:self.clock[0])
        self.assertEqual(other.status_order('blackstock','till-one',order['orderId'])['status'],'awaiting_payment')
        self.assertEqual(other.authorise_mock('blackstock','till-one',order['orderId'])['status'],'authorised')
        self.assertEqual(self.store.complete_mock('blackstock','till-one',order['orderId'])['status'],'confirmed')

    def test_unknown_mock_capture_fails_closed(self):
        order = self.order()
        self.store.authorise_mock('blackstock','till-one',order['orderId'])
        self.store.payment = MockPaymentAdapter(capture=False)
        self.assertEqual(self.store.complete_mock('blackstock','till-one',order['orderId'])['status'],'needs_reconciliation')
        self.assertEqual(self.store.movements('blackstock','a'),[])
        self.fail('ORDER_INVALID_TRANSITION',lambda:self.store.complete_mock('blackstock','till-one',order['orderId']))

    def test_stock_conflict_never_partially_consumes(self):
        order = self.order()
        self.store.authorise_mock('blackstock','till-one',order['orderId'])
        import sqlite3
        with sqlite3.connect(self.path) as db:
            db.execute("UPDATE stock SET qty=1 WHERE venue='blackstock' AND ingredient='corona'")
        self.assertEqual(self.store.complete_mock('blackstock','till-one',order['orderId'])['status'],'needs_reconciliation')
        self.assertEqual(self.store.movements('blackstock','a'),[])

    def test_cannot_plug_real_provider_into_demo(self):
        with self.assertRaises(ValueError):
            SQLiteMockOrders(self.path, payment=object())

    def test_void_failure_requires_reconciliation(self):
        order = self.order()
        self.store.authorise_mock('blackstock','till-one',order['orderId'])
        self.store.payment = MockPaymentAdapter(void=False)
        self.assertEqual(self.store.cancel_mock('blackstock','till-one',order['orderId'])['status'],'needs_reconciliation')
        self.assertEqual(self.store.status('blackstock','a')['status'],'held')

    def test_no_confirmed_order_can_cancel(self):
        order = self.order()
        self.store.authorise_mock('blackstock','till-one',order['orderId'])
        self.store.complete_mock('blackstock','till-one',order['orderId'])
        self.fail('ORDER_INVALID_TRANSITION',lambda:self.store.cancel_mock('blackstock','till-one',order['orderId']))


if __name__ == '__main__':
    unittest.main()
