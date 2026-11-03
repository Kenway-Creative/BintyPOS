"""Trusted-fixture transactional back-office guard; NOT authentication or HTTP.

Guarded data must live in the SAME SQLite database as staff memberships.
The callback is trusted server code, never client-provided or exposed remotely.
"""
from outlet_permissions import AccessDenied, Principal, require_permission
from staff_directory import SQLiteStaffDirectory


class GuardedStaffOperations:
    def __init__(self, path):
        self.directory = SQLiteStaffDirectory(path)
        self.path = path

    def execute_trusted(self, venue, subject, operation, outlet, mutation):
        """Authorise current membership and mutate in one BEGIN IMMEDIATE.

        Revocation or role replacement cannot commit between lookup and write.
        Exceptions roll back. No external side effects in mutation.
        """
        if not callable(mutation):
            raise TypeError('TRUSTED_MUTATION_REQUIRED')
        self.directory._valid(venue)
        self.directory._valid(subject)
        with self.directory._connect() as db:
            db.execute('BEGIN IMMEDIATE')
            row = db.execute(
                'SELECT role FROM staff_memberships WHERE venue=? AND subject=? AND active=1',
                (venue, subject)).fetchone()
            if row is None:
                raise AccessDenied('STAFF_NOT_ACTIVE')
            outlets = frozenset(r[0] for r in db.execute(
                'SELECT outlet FROM staff_outlets WHERE venue=? AND subject=?',
                (venue, subject)))
            principal = Principal(subject, venue, row[0], outlets)
            require_permission(principal, venue, operation, outlet)
            return mutation(db, principal)
