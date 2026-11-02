"""Run with: python3 -m unittest discover -s tests -p 'test_*.py' -v"""
import concurrent.futures
import os
import sqlite3
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from persistent_reservations import SQLiteReservations, ReservationError


class ReservationsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = os.path.join(self.tmp.name, 'reservations.sqlite3')
        self.now = 10000
        self.store = SQLiteReservations(self.db, now=lambda: self.now)
        self.store.bootstrap_stock('blackstock', {'corona': 8, 'vodka': 6, 'ice': 4})

    def tearDown(self):
        self.tmp.cleanup()

    def assert_error(self, code, fn):
        with self.assertRaises(ReservationError) as caught:
            fn()
        self.assertEqual(caught.exception.code, code)

    def test_competing_clients_exactly_one_wins(self):
        def attempt(key):
            client = SQLiteReservations(self.db, now=lambda: self.now)
            try:
                return client.reserve('blackstock', key, {'corona': 5})['status']
            except ReservationError as e:
                return e.code
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            outcomes = list(pool.map(attempt, ['till-a', 'till-b']))
        self.assertCountEqual(outcomes, ['held', 'INSUFFICIENT_RESERVABLE_STOCK'])
        self.assertEqual(self.store.available('blackstock')['corona'], 3)

    def test_reopen_preserves_holds(self):
        self.store.reserve('blackstock', 'a', {'vodka': 4})
        other = SQLiteReservations(self.db, now=lambda: self.now)
        self.assertEqual(other.available('blackstock')['vodka'], 2)
        self.assert_error('INSUFFICIENT_RESERVABLE_STOCK', lambda: other.reserve('blackstock', 'b', {'vodka': 3}))

    def test_commit_once_across_restarts(self):
        self.store.reserve('blackstock', 'a', {'corona': 2, 'ice': 1})
        other = SQLiteReservations(self.db, now=lambda: self.now)
        self.assertEqual(other.commit('blackstock', 'a')['status'], 'committed')
        self.assertEqual(self.store.commit('blackstock', 'a')['status'], 'committed')
        self.assertEqual(self.store.available('blackstock')['corona'], 6)
        self.assertEqual(self.store.available('blackstock')['ice'], 3)
        self.assertEqual(self.store.movements('blackstock', 'a'), [{'ingredient': 'corona', 'qty': 2}, {'ingredient': 'ice', 'qty': 1}])

    def test_idempotent_hold_order_independent(self):
        one = self.store.reserve('blackstock', 'a', {'ice': 1, 'vodka': 2})
        two = self.store.reserve('blackstock', 'a', {'vodka': 2, 'ice': 1})
        self.assertEqual(one, two)

    def test_conflicting_reuse_rejected_after_commit(self):
        self.store.reserve('blackstock', 'a', {'ice': 1})
        self.store.commit('blackstock', 'a')
        self.assert_error('IDEMPOTENCY_CONFLICT', lambda: self.store.reserve('blackstock', 'a', {'ice': 2}))

    def test_release_frees_hold_but_not_committed(self):
        self.store.reserve('blackstock', 'a', {'corona': 8})
        self.assertEqual(self.store.release('blackstock', 'a')['status'], 'released')
        self.assertEqual(self.store.release('blackstock', 'a')['status'], 'released')
        self.assertEqual(self.store.available('blackstock')['corona'], 8)
        self.assert_error('RESERVATION_NOT_ACTIVE', lambda: self.store.commit('blackstock', 'a'))
        self.store.reserve('blackstock', 'b', {'corona': 1})
        self.store.commit('blackstock', 'b')
        self.assert_error('RESERVATION_ALREADY_COMMITTED', lambda: self.store.release('blackstock', 'b'))

    def test_expiry_persists_and_key_cannot_revive(self):
        self.store.reserve('blackstock', 'a', {'corona': 8}, ttl_ms=1000)
        self.now += 1000
        self.assertEqual(self.store.status('blackstock', 'a')['status'], 'expired')
        self.assertEqual(self.store.available('blackstock')['corona'], 8)
        self.assertEqual(self.store.reserve('blackstock', 'a', {'corona': 8})['status'], 'expired')
        self.assert_error('RESERVATION_NOT_ACTIVE', lambda: self.store.commit('blackstock', 'a'))

    def test_insufficient_multicomponent_is_all_or_none(self):
        self.assert_error('INSUFFICIENT_RESERVABLE_STOCK', lambda: self.store.reserve('blackstock', 'a', {'vodka': 2, 'ice': 5}))
        self.assertIsNone(self.store.status('blackstock', 'a'))
        self.assertEqual(self.store.available('blackstock')['vodka'], 6)

    def test_commit_stock_conflict_fails_closed(self):
        self.store.reserve('blackstock', 'a', {'vodka': 5, 'ice': 2})
        with sqlite3.connect(self.db) as db:
            db.execute("UPDATE stock SET qty=1 WHERE venue='blackstock' AND ingredient='ice'")
        self.assert_error('RESERVATION_STOCK_CONFLICT', lambda: self.store.commit('blackstock', 'a'))
        self.assertEqual(self.store.status('blackstock', 'a')['status'], 'conflicted')
        self.assertEqual(self.store.movements('blackstock', 'a'), [])
        self.assertEqual(self.store.available('blackstock')['vodka'], 6)

    def test_venue_isolation(self):
        self.store.bootstrap_stock('other', {'corona': 8})
        self.store.reserve('blackstock', 'same', {'corona': 7})
        self.store.reserve('other', 'same', {'corona': 7})
        self.assertEqual(self.store.available('other')['corona'], 1)
        self.assertEqual(self.store.available('blackstock')['corona'], 1)

    def test_unknown_and_invalid(self):
        self.assert_error('UNKNOWN_RESERVATION', lambda: self.store.commit('blackstock', 'missing'))
        self.assert_error('INVALID_IDEMPOTENCY_KEY', lambda: self.store.reserve('blackstock', '', {}))
        self.assert_error('INVALID_RESERVATION_DEMAND', lambda: self.store.reserve('blackstock', 'a', {'corona': True}))
        self.assert_error('INVALID_RESERVATION_DEMAND', lambda: self.store.reserve('blackstock', 'a', {'corona': -1}))
        self.assert_error('INVALID_RESERVATION_TTL', lambda: self.store.reserve('blackstock', 'a', {}, 0))
        self.assert_error('INVALID_VENUE_ID', lambda: self.store.available('../bad'))

    def test_empty_demand_is_valid_untracked_item(self):
        self.store.reserve('blackstock', 'untracked', {})
        self.assertEqual(self.store.commit('blackstock', 'untracked')['status'], 'committed')
        self.assertEqual(self.store.movements('blackstock', 'untracked'), [])

    def test_bootstrap_never_resets_consumed_stock(self):
        self.store.reserve('blackstock', 'a', {'corona': 3})
        self.store.commit('blackstock', 'a')
        self.store.bootstrap_stock('blackstock', {'corona': 100})
        self.assertEqual(self.store.available('blackstock')['corona'], 5)


if __name__ == '__main__':
    unittest.main()
