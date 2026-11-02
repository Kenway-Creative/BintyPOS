'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const catalog = require('../src/catalog.js');
const keyboards = require('../src/keyboards.js');
const shortcuts = require('../src/shortcuts.js');
const html = fs.readFileSync(path.join(__dirname, '..', 'index.html'), 'utf8');
const inline = 'const seed=' + html.split('<script>\nconst seed=')[1].split('</script>')[0];

function boot() {
  const nodes = {};
  const context = {
    document: { getElementById: id => nodes[id] || (nodes[id] = { innerHTML: '', value: '' }) },
    window: {},
    structuredClone,
    BintyCatalog: catalog,
    BintyKeyboards: keyboards,
    BintyShortcuts: shortcuts
  };
  vm.createContext(context);
  vm.runInContext(inline, context, { timeout: 1000 });
  const run = expression => vm.runInContext(expression, context, { timeout: 1000 });
  return { run, nodes };
}
test('staff till shows published speed keys and one-tap categories', () => {
  const { nodes } = boot();
  assert.match(nodes.app.innerHTML, /Speed keys/);
  assert.match(nodes.app.innerHTML, /★ Corona/);
  assert.match(nodes.app.innerHTML, /Jump to category/);
});
test('one-tap favourite adds to shared basket, preserves order on outlet change', () => {
  const { run } = boot();
  run('quickAdd("corona"); enterFolder("Pattersons"); quickAdd("burger")');
  assert.equal(run('cart.corona'), 1);
  assert.equal(run('cart.burger'), 1);
});
test('category jump resets folder but retains basket', () => {
  const { run } = boot();
  run('quickAdd("burger"); enterFolder("Spuddy Hell"); quickCategory("Food")');
  assert.equal(run('outletFolder'), 'All');
  assert.equal(run('filter'), 'Food');
  assert.equal(run('cart.burger'), 1);
});
test('guest QR has no staff speed-key panel', () => {
  const { run, nodes } = boot();
  run('setTab("qr")');
  assert.doesNotMatch(nodes.app.innerHTML, /aria-label="Speed shortcuts"/);
  assert.match(nodes.app.innerHTML, /Guest QR ordering/);
});
test('restricted area hides disallowed favourite and refuses direct add', () => {
  const { run, nodes } = boot();
  run('setArea("Pattersons")');
  assert.doesNotMatch(nodes.app.innerHTML, /★ Corona/);
  run('quickAdd("corona")');
  assert.equal(run('cart.corona'), undefined);
});
test('draft changes do not show on till before publication', () => {
  const { run, nodes } = boot();
  run('setTab("backoffice")');
  nodes.demoPin = { value: '2468' };
  run('unlockDemo(); toggleShortcut("productIds","cake"); setTab("till")');
  assert.doesNotMatch(nodes.app.innerHTML, /★ Cherry On Top Cake/);
  assert.equal(run('shortcutStore.published("Main Bar").version'), 1);
});
test('published shortcut becomes available without changing existing basket', () => {
  const { run, nodes } = boot();
  run('quickAdd("corona"); setTab("backoffice")');
  nodes.demoPin = { value: '2468' };
  run('unlockDemo(); toggleShortcut("productIds","cake"); publishShortcuts(); setTab("till")');
  assert.match(nodes.app.innerHTML, /★ Cherry On Top Cake/);
  assert.equal(run('shortcutStore.published("Main Bar").version'), 2);
  assert.equal(run('cart.corona'), 1);
});
test('out-of-stock speed key is disabled and cannot add more', () => {
  const { run, nodes } = boot();
  run('stock.corona=0; render()');
  assert.match(nodes.app.innerHTML, /class="speed-key" disabled/);
  run('quickAdd("corona")');
  assert.equal(run('cart.corona'), undefined);
});
