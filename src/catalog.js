/* BintyPOS catalogue projection v0.2.1. Pure, dependency-free and safe for Node/browser demos.
 * Presentation-only filtering; NOT a server-side authorisation boundary.
 */
(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  root.BintyCatalog = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';
  const SHORT_MENU_IDS = Object.freeze(['corona', 'burger', 'fries', 'cake']);

  function inArea(product, areaMode) {
    if (areaMode === 'All') return true;
    if (areaMode === 'Short Menu') return SHORT_MENU_IDS.includes(product.id);
    if (Array.isArray(areaMode)) return areaMode.includes(product.vendor);
    return product.vendor === areaMode;
  }

  function project(products, options = {}) {
    const areaMode = options.areaMode === undefined ? 'All' : options.areaMode;
    const outlet = options.channel === 'guest' ? 'All' : (options.outlet || 'All');
    const category = options.category || 'All';
    const query = String(options.search || '').trim().toLocaleLowerCase('en-GB');
    return products.filter(product =>
      inArea(product, areaMode) &&
      (outlet === 'All' || product.vendor === outlet) &&
      (category === 'All' || product.category === category) &&
      (!query || product.name.toLocaleLowerCase('en-GB').includes(query))
    );
  }

  function categories(products, options = {}) {
    return [...new Set(project(products, { ...options, category: 'All', search: '' }).map(p => p.category))];
  }

  function outlets(products, areaMode = 'All') {
    return [...new Set(project(products, { areaMode, channel: 'guest' }).map(p => p.vendor))];
  }

  return Object.freeze({ project, categories, outlets, inArea });
});
