"""Run: python -m unittest discover -s tests -p 'test_*.py' -v"""
import concurrent.futures
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from trusted_checkout import TrustedQuoteReservations
from persistent_reservations import ReservationError


class TrustedCheckoutTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = os.path.join(self.tmp.name, 'stock.db')
        self.clock = [10000]
        self.store = TrustedQuoteReservations(self.db, now=lambda: self.clock[0])
        self.store.bootstrap_stock('blackstock', {'corona': 8, 'ice': 5})
        self.store.publish_product('blackstock', 'beer', 'bar', 450, {'corona': 1})
        self.store.publish_product('blackstock', 'bucket', 'bar', 2000, {'corona': 5, 'ice': 1})

    def tearDown(self):
        self.tmp.cleanup()

    def fail_code(self, code, action):
        with self.assertRaises(ReservationError) as ctx:
            action()
        self.assertEqual(ctx.exception.code, code)

    def quote(self, lines=None, session='till-one', venue='blackstock'):
        return self.store.create_quote(venue, session, lines or [{'productId':'beer','quantity':2}])

    def accept(self, q, session='till-one'):
        return self.store.accept_quote(q['venue'],session,q['quoteId'],q['totalMinor'])

    def test_server_price_and_recipe_not_client_fields(self):
        q = self.quote([{'productId':'beer','quantity':3}])
        self.assertEqual(q['totalMinor'], 1350)
        self.assertEqual(q['lines'][0]['businessId'], 'bar')
        self.assertEqual(q['lines'][0]['version'], 1)
        self.accept(q)
        held = self.store.reserve_accepted_quote('blackstock','till-one',q['quoteId'],'a')
        self.assertEqual(held['demands'], {'corona':3})
        self.assertEqual(self.store.available('blackstock')['corona'], 5)

    def test_multi_product_shared_ingredient_aggregate(self):
        q = self.quote([{'productId':'beer','quantity':4},{'productId':'bucket','quantity':1}])
        self.accept(q)
        self.fail_code('INSUFFICIENT_RESERVABLE_STOCK',lambda: self.store.reserve_accepted_quote('blackstock','till-one',q['quoteId'],'a'))
        self.assertEqual(self.store.available('blackstock')['corona'],8)

    def test_unaccepted_quote_cannot_hold(self):
        q = self.quote()
        self.fail_code('QUOTE_NOT_ACCEPTED',lambda: self.store.reserve_accepted_quote('blackstock','till-one',q['quoteId'],'a'))

    def test_wrong_session_rejected(self):
        q = self.quote()
        self.fail_code('QUOTE_SESSION_MISMATCH',lambda: self.store.accept_quote('blackstock','other',q['quoteId'],q['totalMinor']))
        self.accept(q)
        self.fail_code('QUOTE_SESSION_MISMATCH',lambda: self.store.reserve_accepted_quote('blackstock','other',q['quoteId'],'a'))

    def test_wrong_total_rejected(self):
        q = self.quote()
        self.fail_code('QUOTE_TOTAL_CONFLICT',lambda: self.store.accept_quote('blackstock','till-one',q['quoteId'],1))

    def test_republished_product_stales_quote(self):
        q = self.quote()
        self.store.publish_product('blackstock','beer','bar',550,{'corona':1})
        self.fail_code('STALE_QUOTE',lambda: self.accept(q))
        fresh = self.quote()
        self.accept(fresh)
        self.store.publish_product('blackstock','beer','bar',550,{'corona':2})
        self.fail_code('STALE_QUOTE',lambda: self.store.reserve_accepted_quote('blackstock','till-one',fresh['quoteId'],'new'))

    def test_quote_expiry(self):
        q = self.store.create_quote('blackstock','till-one',[{'productId':'beer','quantity':1}],1000)
        self.clock[0] += 1000
        self.fail_code('QUOTE_EXPIRED',lambda: self.accept(q))

    def test_idempotent_replay_and_no_second_hold(self):
        q = self.quote()
        self.accept(q)
        first = self.store.reserve_accepted_quote('blackstock','till-one',q['quoteId'],'a')
        self.assertEqual(first,self.store.reserve_accepted_quote('blackstock','till-one',q['quoteId'],'a'))
        self.fail_code('QUOTE_ALREADY_RESERVED',lambda: self.store.reserve_accepted_quote('blackstock','till-one',q['quoteId'],'b'))
        self.assertEqual(self.store.available('blackstock')['corona'],6)

    def test_key_cannot_be_reused_for_other_quote(self):
        q1,q2 = self.quote(),self.quote()
        self.accept(q1)
        self.accept(q2)
        self.store.reserve_accepted_quote('blackstock','till-one',q1['quoteId'],'a')
        self.fail_code('IDEMPOTENCY_CONFLICT',lambda: self.store.reserve_accepted_quote('blackstock','till-one',q2['quoteId'],'a'))

    def test_durable_restart_and_commit_once(self):
        q = self.quote()
        self.accept(q)
        self.store.reserve_accepted_quote('blackstock','till-one',q['quoteId'],'a')
        other = TrustedQuoteReservations(self.db,now=lambda:self.clock[0])
        self.assertEqual(other.reserve_accepted_quote('blackstock','till-one',q['quoteId'],'a')['status'],'held')
        self.assertEqual(other.commit('blackstock','a')['status'],'committed')
        self.assertEqual(other.commit('blackstock','a')['status'],'committed')
        self.assertEqual(other.movements('blackstock','a'),[{'ingredient':'corona','qty':2}])

    def test_competing_quotes_atomic(self):
        q1 = self.quote([{'productId':'bucket','quantity':1}])
        q2 = self.quote([{'productId':'bucket','quantity':1}],session='till-two')
        self.accept(q1)
        self.accept(q2,'till-two')
        def attempt(pair):
            q,session,key = pair
            other = TrustedQuoteReservations(self.db,now=lambda:self.clock[0])
            try:
                return other.reserve_accepted_quote('blackstock',session,q['quoteId'],key)['status']
            except ReservationError as err:
                return err.code
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            outcomes = list(pool.map(attempt,[(q1,'till-one','a'),(q2,'till-two','b')]))
        self.assertCountEqual(outcomes,['held','INSUFFICIENT_RESERVABLE_STOCK'])

    def test_rejects_untrusted_fields_and_invalid_values(self):
        self.fail_code('INVALID_QUOTE_LINES',lambda:self.quote([{'productId':'beer','quantity':1,'priceMinor':1}]))
        self.fail_code('INVALID_QUOTE_LINES',lambda:self.quote([{'productId':'beer','quantity':True}]))
        self.fail_code('INVALID_QUOTE_LINES',lambda:self.quote([{'productId':'beer','quantity':-1}]))
        self.fail_code('PRODUCT_UNAVAILABLE',lambda:self.quote([{'productId':'missing','quantity':1}]))
        self.fail_code('INVALID_RESERVATION_DEMAND',lambda:self.store.publish_product('blackstock','bad','bar',1,{'ice':True}))

    def test_venue_scoped(self):
        q = self.quote()
        self.fail_code('UNKNOWN_QUOTE',lambda:self.store.accept_quote('other','till-one',q['quoteId'],q['totalMinor']))
        self.fail_code('INVALID_CHECKOUT_SESSION',lambda:self.store.create_quote('blackstock','INVALID',[]))

    def test_unavailable_product_rejected(self):
        self.store.publish_product('blackstock','beer','bar',450,{'corona':1},False)
        self.fail_code('PRODUCT_UNAVAILABLE',lambda:self.quote())


if __name__ == '__main__':
    unittest.main()
