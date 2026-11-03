"""Scoped, revocable demo checkout capabilities; never a real login/payment service."""
import hashlib
import os
import sqlite3
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from checkout_identity import ScopedDemoCheckout
from persistent_reservations import ReservationError


class CheckoutIdentityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmp.name, 'demo.sqlite')
        self.clock = [10000]
        self.api = ScopedDemoCheckout(self.path, now=lambda: self.clock[0])
        self.api._orders.bootstrap_stock('blackstock', {'corona': 10})
        self.api._orders.publish_product('blackstock', 'beer', 'bar', 450, {'corona': 1})
        self.staff = self.api.bootstrap_demo_identity('blackstock', 'staff')['token']
        self.qr = self.api.bootstrap_demo_identity('blackstock', 'qr')['token']

    def tearDown(self):
        self.tmp.cleanup()

    def fails(self, code, action):
        with self.assertRaises(ReservationError) as ctx:
            action()
        self.assertEqual(ctx.exception.code, code)

    def test_scoped_quote_to_order_and_mock_service_completion(self):
        q = self.api.create_quote('blackstock', self.staff, [{'productId':'beer','quantity':2}])
        self.assertEqual(q['totalMinor'], 900)
        self.api.accept_quote('blackstock', self.staff, q['quoteId'], 900)
        order = self.api.create_order('blackstock', self.staff, q['quoteId'], 'one')
        self.assertEqual(self.api.status_order('blackstock', self.staff, order['orderId'])['status'], 'awaiting_payment')
        self.assertFalse(hasattr(self.api, 'authorise_mock'))
        self.assertFalse(hasattr(self.api, 'complete_mock'))
        self.assertFalse(hasattr(self.api, 'commit'))
        # Trusted test service, never a checkout token operation:
        session = self._stored_session(self.staff)
        self.api._orders.authorise_mock('blackstock', session, order['orderId'])
        self.api._orders.complete_mock('blackstock', session, order['orderId'])
        self.assertEqual(self.api.status_order('blackstock', self.staff, order['orderId'])['status'], 'confirmed')
        self.assertEqual(self.api._orders.available('blackstock')['corona'], 8)

    def _stored_session(self, token):
        with sqlite3.connect(self.path) as db:
            return db.execute('SELECT session_id FROM demo_checkout_capabilities WHERE token_digest=?',
                              (hashlib.sha256(token.encode()).hexdigest(),)).fetchone()[0]

    def test_token_not_stored_in_plaintext(self):
        with sqlite3.connect(self.path) as db:
            digest, session = db.execute('SELECT token_digest,session_id FROM demo_checkout_capabilities WHERE channel="staff"').fetchone()
        self.assertEqual(digest, hashlib.sha256(self.staff.encode()).hexdigest())
        self.assertNotEqual(digest, self.staff)
        self.assertNotEqual(session, self.staff)

    def test_unrecognised_or_malformed_token_fails_closed(self):
        for token in ('bad', 'x'*43, None, '☃'*40):
            self.fails('CHECKOUT_UNAUTHENTICATED', lambda token=token:self.api.create_quote('blackstock', token, [{'productId':'beer','quantity':1}]))

    def test_venue_mismatch_denied_even_with_valid_token(self):
        self.fails('CHECKOUT_UNAUTHENTICATED',lambda:self.api.create_quote('other',self.staff,[{'productId':'beer','quantity':1}]))

    def test_quote_cannot_be_stolen_by_other_valid_token(self):
        q = self.api.create_quote('blackstock',self.staff,[{'productId':'beer','quantity':1}])
        self.fails('QUOTE_SESSION_MISMATCH',lambda:self.api.accept_quote('blackstock',self.qr,q['quoteId'],q['totalMinor']))

    def test_order_cannot_be_read_by_other_valid_token(self):
        q = self.api.create_quote('blackstock',self.staff,[{'productId':'beer','quantity':1}])
        self.api.accept_quote('blackstock',self.staff,q['quoteId'],q['totalMinor'])
        o = self.api.create_order('blackstock',self.staff,q['quoteId'],'one')
        self.fails('ORDER_SESSION_MISMATCH',lambda:self.api.status_order('blackstock',self.qr,o['orderId']))

    def test_guest_cannot_cancel_even_own_order(self):
        q = self.api.create_quote('blackstock',self.qr,[{'productId':'beer','quantity':1}])
        self.api.accept_quote('blackstock',self.qr,q['quoteId'],q['totalMinor'])
        o = self.api.create_order('blackstock',self.qr,q['quoteId'],'guest')
        self.fails('CHECKOUT_FORBIDDEN',lambda:self.api.cancel_mock('blackstock',self.qr,o['orderId']))
        self.assertEqual(self.api.status_order('blackstock',self.qr,o['orderId'])['status'],'awaiting_payment')

    def test_staff_can_cancel_own_unpaid_order(self):
        q = self.api.create_quote('blackstock',self.staff,[{'productId':'beer','quantity':1}])
        self.api.accept_quote('blackstock',self.staff,q['quoteId'],q['totalMinor'])
        o = self.api.create_order('blackstock',self.staff,q['quoteId'],'one')
        self.assertEqual(self.api.cancel_mock('blackstock',self.staff,o['orderId'])['status'],'released')

    def test_revocation_is_durable(self):
        self.api.revoke_demo_identity('blackstock',self.staff)
        other = ScopedDemoCheckout(self.path,now=lambda:self.clock[0])
        self.fails('CHECKOUT_UNAUTHENTICATED',lambda:other.create_quote('blackstock',self.staff,[{'productId':'beer','quantity':1}]))

    def test_expiry_fails_closed(self):
        short = self.api.bootstrap_demo_identity('blackstock','qr',1000)['token']
        self.clock[0] += 1000
        self.fails('CHECKOUT_UNAUTHENTICATED',lambda:self.api.create_quote('blackstock',short,[{'productId':'beer','quantity':1}]))

    def test_valid_token_survives_process_restart(self):
        other = ScopedDemoCheckout(self.path,now=lambda:self.clock[0])
        self.assertEqual(other.create_quote('blackstock',self.staff,[{'productId':'beer','quantity':1}])['totalMinor'],450)

    def test_invalid_channel_and_ttl(self):
        self.fails('INVALID_CHECKOUT_CHANNEL',lambda:self.api.bootstrap_demo_identity('blackstock','admin'))
        self.fails('INVALID_CHECKOUT_TTL',lambda:self.api.bootstrap_demo_identity('blackstock','staff',True))
        self.fails('INVALID_CHECKOUT_TTL',lambda:self.api.bootstrap_demo_identity('blackstock','staff',999))

    def test_wrong_venue_cannot_revoke(self):
        self.fails('CHECKOUT_UNAUTHENTICATED',lambda:self.api.revoke_demo_identity('other',self.staff))
        self.assertEqual(self.api.create_quote('blackstock',self.staff,[{'productId':'beer','quantity':1}])['totalMinor'],450)


if __name__ == '__main__':
    unittest.main()
