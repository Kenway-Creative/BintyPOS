"""Loopback-only HTTP staff-scope smoke and security regressions."""
import http.client
import os
import sys
import tempfile
import threading
import unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from demo_http import create_demo_server
from staff_sessions import DemoStaffSessions


class HttpTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmp.name, 'fixture.sqlite')
        sessions = DemoStaffSessions(self.path)
        sessions.directory.enrol_trusted('blackstock', 'alice', 'outlet_manager', ('spuddy',))
        self.token = sessions.provision_trusted('blackstock', 'alice')
        self.sessions = sessions
        self.server = create_demo_server(self.path)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)
        self.tmp.cleanup()

    def request(self, path, token=None, method='GET'):
        conn = http.client.HTTPConnection('127.0.0.1', self.server.server_port, timeout=3)
        headers = {'Authorization': 'Bearer ' + token} if token is not None else {}
        conn.request(method, path, headers=headers)
        response = conn.getresponse()
        body = response.read().decode()
        status = response.status
        cache = response.getheader('Cache-Control')
        conn.close()
        return status, body, cache

    def test_allowed_scope(self):
        status, body, cache = self.request('/api/v1/venues/blackstock/outlets/spuddy/staff-access', self.token)
        self.assertEqual(status, 200)
        self.assertIn('"subject":"alice"', body)
        self.assertEqual(cache, 'no-store')

    def test_cross_outlet_and_venue_denied(self):
        for path in ('/api/v1/venues/blackstock/outlets/bar/staff-access',
                     '/api/v1/venues/other/outlets/spuddy/staff-access'):
            self.assertEqual(self.request(path, self.token)[0], 403)

    def test_missing_forged_revoked_and_role_change(self):
        path = '/api/v1/venues/blackstock/outlets/spuddy/staff-access'
        self.assertEqual(self.request(path)[0], 401)
        self.assertEqual(self.request(path, '0' * 64)[0], 403)
        self.sessions.directory.enrol_trusted('blackstock', 'alice', 'staff', ('spuddy',))
        self.assertEqual(self.request(path, self.token)[0], 200)
        self.sessions.directory.revoke_trusted('blackstock', 'alice')
        self.assertEqual(self.request(path, self.token)[0], 403)

    def test_no_mutations_or_query_parameter_auth(self):
        path = '/api/v1/venues/blackstock/outlets/spuddy/staff-access'
        self.assertEqual(self.request(path, self.token, 'POST')[0], 405)
        self.assertEqual(self.request(path + '?token=' + self.token)[0], 404)

    def test_duplicate_and_oversized_authorization_rejected(self):
        path = '/api/v1/venues/blackstock/outlets/spuddy/staff-access'
        for values in (['Bearer ' + self.token, 'Bearer ' + self.token],
                       ['Bearer ' + 'x' * 200]):
            conn = http.client.HTTPConnection('127.0.0.1', self.server.server_port, timeout=3)
            conn.putrequest('GET', path)
            for value in values:
                conn.putheader('Authorization', value)
            conn.endheaders()
            response = conn.getresponse()
            self.assertEqual(response.status, 401)
            response.read()
            conn.close()

    def test_loopback_only(self):
        with self.assertRaises(ValueError):
            create_demo_server(self.path, host='0.0.0.0')


if __name__ == '__main__':
    unittest.main()
