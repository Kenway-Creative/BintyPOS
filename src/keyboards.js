/* BintyPOS keyboard profiles v0.2.2.
 * Pure in-memory prototype: drafts never affect published till/QR projections.
 * Not authentication, persistence, or a server-side authorisation boundary.
 */
(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  root.BintyKeyboards = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  const copy = value => JSON.parse(JSON.stringify(value));

  function normalise(input, knownVendors) {
    let kind, vendors;
    if (input === 'All') { kind = 'all'; vendors = []; }
    else if (input === 'Short Menu') { kind = 'short'; vendors = []; }
    else if (typeof input === 'string') { kind = 'vendors'; vendors = [input]; }
    else if (Array.isArray(input)) { kind = 'vendors'; vendors = input; }
    else if (input && typeof input === 'object') {
      kind = input.kind;
      vendors = input.vendors || [];
    } else throw new Error('INVALID_KEYBOARD_PROFILE');

    if (!['all', 'short', 'vendors'].includes(kind) || !Array.isArray(vendors)) {
      throw new Error('INVALID_KEYBOARD_PROFILE');
    }
    if (kind !== 'vendors' && vendors.length) throw new Error('UNEXPECTED_VENDORS');
    if (kind === 'vendors') {
      if (!vendors.length) throw new Error('EMPTY_OUTLET_SELECTION');
      if (vendors.some(v => typeof v !== 'string' || !v.trim())) throw new Error('INVALID_OUTLET');
      if (new Set(vendors).size !== vendors.length) throw new Error('DUPLICATE_OUTLET');
      if (knownVendors.size && vendors.some(v => !knownVendors.has(v))) throw new Error('UNKNOWN_OUTLET');
    }
    return { kind, vendors: [...vendors] };
  }

  function areaMode(profile) {
    if (!profile) throw new Error('UNKNOWN_AREA');
    if (profile.kind === 'all') return 'All';
    if (profile.kind === 'short') return 'Short Menu';
    if (profile.kind === 'vendors') return [...profile.vendors];
    throw new Error('INVALID_KEYBOARD_PROFILE');
  }

  function createStore(initial, options = {}) {
    if (!initial || typeof initial !== 'object' || Array.isArray(initial)) throw new Error('INVALID_AREAS');
    const known = new Set(options.vendors || []);
    const published = new Map();
    const drafts = new Map();
    const history = [];
    for (const [areaId, input] of Object.entries(initial)) {
      if (!areaId.trim()) throw new Error('INVALID_AREA');
      published.set(areaId, { version: 1, ...normalise(input, known) });
    }
    function requireArea(areaId) {
      if (!published.has(areaId)) throw new Error('UNKNOWN_AREA');
      return published.get(areaId);
    }
    return Object.freeze({
      areas: () => [...published.keys()],
      published: areaId => copy(requireArea(areaId)),
      draft: areaId => { requireArea(areaId); return drafts.has(areaId) ? copy(drafts.get(areaId)) : null; },
      stage: (areaId, input) => {
        const current = requireArea(areaId);
        const draft = { baseVersion: current.version, ...normalise(input, known) };
        drafts.set(areaId, draft);
        return copy(draft);
      },
      discard: areaId => { requireArea(areaId); drafts.delete(areaId); },
      publish: (areaId, expectedVersion) => {
        const current = requireArea(areaId);
        if (!Number.isInteger(expectedVersion) || expectedVersion !== current.version) throw new Error('KEYBOARD_VERSION_CONFLICT');
        const draft = drafts.get(areaId);
        if (!draft) throw new Error('NO_PENDING_DRAFT');
        if (draft.baseVersion !== current.version) throw new Error('KEYBOARD_VERSION_CONFLICT');
        const next = { version: current.version + 1, kind: draft.kind, vendors: [...draft.vendors] };
        published.set(areaId, next);
        drafts.delete(areaId);
        history.push({ areaId, ...copy(next) });
        return copy(next);
      },
      history: () => copy(history)
    });
  }
  return Object.freeze({ createStore, areaMode, normalise });
});
