"""Loopback-only, read-only staff scope probe. Demo capabilities are NOT login."""
import json
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit
from staff_sessions import DemoStaffSessions
from outlet_permissions import AccessDenied

ROUTE = re.compile(r'^/api/v1/venues/([A-Za-z0-9_-]{1,64})/outlets/([A-Za-z0-9_-]{1,64})/staff-access$')


def make_handler(database_path):
    sessions = DemoStaffSessions(database_path)

    class Handler(BaseHTTPRequestHandler):
        server_version = 'BintyPOS-demo'
        sys_version = ''

        def _reply(self, status, payload):
            data = json.dumps(payload, separators=(',', ':')).encode('utf-8')
            self.send_response(status)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(data)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            parsed = urlsplit(self.path)
            match = ROUTE.fullmatch(parsed.path)
            if not match or parsed.query or parsed.fragment:
                return self._reply(404, {'error': 'NOT_FOUND'})
            # Fail closed on Host ambiguity and DNS-rebinding-style requests.
            hosts = self.headers.get_all('Host', [])
            expected = {f'127.0.0.1:{self.server.server_port}', f'localhost:{self.server.server_port}'}
            if len(hosts) != 1 or hosts[0] not in expected:
                return self._reply(400, {'error': 'INVALID_HOST'})
            # No browser clients are authorised: reject Origin even for loopback requests.
            # A future browser integration needs explicit origin policy and CSRF review.
            if self.headers.get_all('Origin', []):
                return self._reply(403, {'error': 'BROWSER_ORIGIN_DENIED'})
            if any(v.lower() not in ('none', 'same-origin') for v in self.headers.get_all('Sec-Fetch-Site', [])):
                return self._reply(403, {'error': 'BROWSER_ORIGIN_DENIED'})
            headers = self.headers.get_all('Authorization', [])
            if len(headers) != 1 or len(headers[0]) > 128:
                return self._reply(401, {'error': 'UNAUTHORISED'})
            header = headers[0]
            parts = header.split(' ')
            if len(parts) != 2 or parts[0] != 'Bearer' or not parts[1]:
                return self._reply(401, {'error': 'UNAUTHORISED'})
            venue, outlet = match.groups()
            try:
                def projection(_db, principal):
                    return {'venueId': venue, 'outletId': outlet, 'subject': principal.subject,
                            'role': principal.role, 'allowed': True}
                result = sessions.execute(venue, parts[1], 'stock.count.read', outlet, projection)
            except (AccessDenied, ValueError):
                return self._reply(403, {'error': 'ACCESS_DENIED'})
            return self._reply(200, result)

        def do_POST(self):
            self._reply(405, {'error': 'METHOD_NOT_ALLOWED'})

        def do_PUT(self):
            self._reply(405, {'error': 'METHOD_NOT_ALLOWED'})

        def do_DELETE(self):
            self._reply(405, {'error': 'METHOD_NOT_ALLOWED'})

        def log_message(self, _format, *_args):
            pass

    return Handler


def create_demo_server(database_path, host='127.0.0.1', port=0):
    if host not in ('127.0.0.1', '::1'):
        raise ValueError('LOOPBACK_ONLY')
    return ThreadingHTTPServer((host, port), make_handler(database_path))


if __name__ == '__main__':
    raise SystemExit('No CLI listener: provision a trusted fixture and start create_demo_server explicitly.')
