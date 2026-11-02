/* BintyPOS speed shortcuts v0.2.3. Pure in-memory prototype.
 * Presentation only: NEVER a stock, price, or authorisation boundary.
 */
(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  root.BintyShortcuts = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';
  const copy = value => JSON.parse(JSON.stringify(value));
  const MAX_FAVOURITES = 8;
  const MAX_CATEGORIES = 6;

  function normalise(input, products) {
    if (!input || typeof input !== 'object' || Array.isArray(input)) throw new Error('INVALID_SHORTCUTS');
    const productIds = input.productIds === undefined ? [] : input.productIds;
    const categories = input.categories === undefined ? [] : input.categories;
    if (!Array.isArray(productIds) || !Array.isArray(categories)) throw new Error('INVALID_SHORTCUTS');
    if (productIds.length > MAX_FAVOURITES || categories.length > MAX_CATEGORIES) throw new Error('SHORTCUT_LIMIT');
    for (const [values, allowed, error] of [
      [productIds, new Set(products.map(p => p.id)), 'UNKNOWN_PRODUCT'],
      [categories, new Set(products.map(p => p.category)), 'UNKNOWN_CATEGORY']
    ]) {
      if (values.some(v => typeof v !== 'string' || !v.trim() || !allowed.has(v))) throw new Error(error);
      if (new Set(values).size !== values.length) throw new Error('DUPLICATE_SHORTCUT');
    }
    return { productIds: [...productIds], categories: [...categories] };
  }

  function createStore(initial, options = {}) {
    if (!Array.isArray(options.areas) || !Array.isArray(options.products)) throw new Error('INVALID_SHORTCUT_STORE');
    const areas = new Set(options.areas);
    if (areas.size !== options.areas.length) throw new Error('DUPLICATE_AREA');
    const published = new Map(), drafts = new Map(), history = [];
    for (const area of areas) {
      if (typeof area !== 'string' || !area.trim()) throw new Error('INVALID_AREA');
      published.set(area, { version: 1, ...normalise((initial || {})[area] || {}, options.products) });
    }
    function requireArea(area) {
      if (!published.has(area)) throw new Error('UNKNOWN_AREA');
      return published.get(area);
    }
    return Object.freeze({
      areas: () => [...areas],
      published: area => copy(requireArea(area)),
      draft: area => { requireArea(area); return drafts.has(area) ? copy(drafts.get(area)) : null; },
      stage: (area, input) => {
        const current = requireArea(area);
        const next = { baseVersion: current.version, ...normalise(input, options.products) };
        drafts.set(area, next);
        return copy(next);
      },
      discard: area => { requireArea(area); drafts.delete(area); },
      publish: (area, expectedVersion) => {
        const current = requireArea(area);
        if (!Number.isInteger(expectedVersion) || current.version !== expectedVersion) throw new Error('SHORTCUT_VERSION_CONFLICT');
        const draft = drafts.get(area);
        if (!draft) throw new Error('NO_PENDING_DRAFT');
        if (draft.baseVersion !== current.version) throw new Error('SHORTCUT_VERSION_CONFLICT');
        const next = { version: current.version + 1, productIds: [...draft.productIds], categories: [...draft.categories] };
        published.set(area, next);
        drafts.delete(area);
        history.push({ area, ...copy(next) });
        return copy(next);
      },
      history: () => copy(history)
    });
  }

  function visible(products, areaMode, profile, catalog) {
    if (!profile || !catalog || typeof catalog.project !== 'function') throw new Error('INVALID_PROJECTION');
    const allowed = catalog.project(products, { areaMode, channel: 'staff' });
    const byId = new Map(allowed.map(p => [p.id, p]));
    const allowedCategories = new Set(allowed.map(p => p.category));
    return {
      favourites: profile.productIds.map(id => byId.get(id)).filter(Boolean),
      categories: profile.categories.filter(category => allowedCategories.has(category))
    };
  }
  return Object.freeze({ createStore, normalise, visible, MAX_FAVOURITES, MAX_CATEGORIES });
});