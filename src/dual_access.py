"""Atomic demo staff + device scope guard. Trusted Python only; no HTTP or payments."""
import time
from device_registry import DemoDeviceRegistry
from staff_sessions import DemoStaffSessions
from outlet_permissions import AccessDenied


class DemoDualAccess:
    """Both capabilities must be active for the same venue and outlet.

    Device lookup shares the staff session's BEGIN IMMEDIATE transaction, so
    revocation/rotation cannot race between verification and projection.
    Device credentials alone never authorise an operation.
    """
    def __init__(self, path):
        self.devices = DemoDeviceRegistry(path)
        self.sessions = DemoStaffSessions(path)

    def read_trusted(self, venue, outlet, staff_token, device_token):
        self.sessions.directory._valid(outlet)
        device_digest = self.devices._digest(device_token)

        def projection(db, principal):
            row = db.execute("""SELECT device_id, outlet FROM demo_devices
                WHERE digest=? AND venue=? AND revoked=0 AND expires_at>?""",
                (device_digest, venue, int(time.time()))).fetchone()
            if row is None or row[1] != outlet:
                raise AccessDenied('DEVICE_SCOPE_DENIED')
            return {'venueId': venue, 'outletId': outlet, 'subject': principal.subject,
                    'role': principal.role, 'deviceId': row[0], 'allowed': True}

        return self.sessions.execute(venue, staff_token, 'stock.count.read',
                                     outlet, projection)
