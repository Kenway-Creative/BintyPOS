"""Server-side outlet authorisation policy prototype. NOT identity verification.

Caller must supply a trusted, server-resolved Principal; never construct from
client claims, QR parameters or demo PINs. No HTTP or payment authority.
"""
from dataclasses import dataclass

class AccessDenied(PermissionError):
    pass

@dataclass(frozen=True)
class Principal:
    subject: str
    venue: str
    role: str
    outlets: frozenset[str] = frozenset()

    def __post_init__(self):
        if not isinstance(self.subject, str) or not self.subject.strip() or not isinstance(self.venue, str) or not self.venue.strip():
            raise ValueError('INVALID_PRINCIPAL')
        if self.role not in ('venue_admin', 'outlet_manager', 'staff'):
            raise ValueError('INVALID_ROLE')
        if not isinstance(self.outlets, frozenset) or any(not isinstance(o, str) or not o.strip() for o in self.outlets):
            raise ValueError('INVALID_OUTLET_SCOPE')

VENUE_ACTIONS = frozenset({'catalogue.approve', 'keyboard.publish', 'stock.count.review', 'reconciliation.review'})
OUTLET_ACTIONS = {
    'outlet.offering.propose': frozenset({'venue_admin', 'outlet_manager'}),
    'stock.count.submit': frozenset({'venue_admin', 'outlet_manager'}),
    'stock.count.read': frozenset({'venue_admin', 'outlet_manager', 'staff'}),
}

def require_permission(principal, venue, operation, outlet=None):
    """Fail closed; an explicit outlet is required for outlet actions."""
    if not isinstance(principal, Principal):
        raise AccessDenied('UNVERIFIED_PRINCIPAL')
    if not isinstance(venue, str) or not venue or principal.venue != venue:
        raise AccessDenied('VENUE_SCOPE_DENIED')
    if not isinstance(operation, str):
        raise AccessDenied('OPERATION_DENIED')
    if operation in OUTLET_ACTIONS:
        if not isinstance(outlet, str) or not outlet.strip():
            raise AccessDenied('OUTLET_REQUIRED')
        if principal.role not in OUTLET_ACTIONS[operation]:
            raise AccessDenied('OPERATION_DENIED')
        if principal.role != 'venue_admin' and outlet not in principal.outlets:
            raise AccessDenied('OUTLET_SCOPE_DENIED')
        return True
    if outlet is not None:
        raise AccessDenied('UNEXPECTED_OUTLET_SCOPE')
    if principal.role == 'venue_admin' and operation in VENUE_ACTIONS:
        return True
    raise AccessDenied('OPERATION_DENIED')
