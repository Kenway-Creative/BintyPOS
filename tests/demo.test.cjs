'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const html = fs.readFileSync(path.join(root, 'index.html'), 'utf8');

test('demo loads shared catalogue before application script', () => {
  assert.match(html, /<script src="\.\/src\/catalog\.js"><\/script>\s*<script src="\.\/src\/keyboards\.js"><\/script>\s*<script src="\.\/src\/shortcuts\.js"><\/script>\s*<script src="\.\/src\/offerings\.js"><\/script>\s*<script src="\.\/src\/basket\.js"><\/script>\s*<script>/);
});
test('application JavaScript parses', () => {
  const parts = html.split('<script>\nconst seed=');
  assert.equal(parts.length, 2);
  const inline = 'const seed=' + parts[1].split('</script>')[0];
  assert.doesNotThrow(() => new Function(inline));
});
test('both staff and QR use the shared catalogue projection', () => {
  assert.match(html, /BintyCatalog\.project\(products/);
  assert.match(html, /channel:guest\?'guest':'staff'/);
  assert.match(html, /BintyCatalog\.categories\(products/);
  assert.match(html, /BintyCatalog\.outlets\(products/);
});

test('demo loads keyboard profiles before application script', () => {
  assert.match(html, /<script src="\.\/src\/catalog\.js"><\/script>\s*<script src="\.\/src\/keyboards\.js"><\/script>\s*<script src="\.\/src\/shortcuts\.js"><\/script>\s*<script src="\.\/src\/offerings\.js"><\/script>\s*<script src="\.\/src\/basket\.js"><\/script>\s*<script>/);
});
test('till and QR use only published keyboard profiles', () => {
  assert.match(html, /BintyKeyboards\.areaMode\(keyboardStore\.published\(areaId\)\)/);
  assert.match(html, /function publishKeyboard\(\)/);
  assert.match(html, /keyboardStore\.publish\(area,keyboardStore\.published\(area\)\.version\)/);
  assert.match(html, /function discardKeyboard\(\)/);
});

test('speed shortcut module loads before inline app', () => {
  assert.match(html, /<script src="\.\/src\/shortcuts\.js"><\/script>\s*<script src="\.\/src\/offerings\.js"><\/script>\s*<script src="\.\/src\/basket\.js"><\/script>\s*<script>/);
  assert.match(html, /BintyShortcuts\.createStore\(/);
  assert.match(html, /BintyShortcuts\.visible\(products,liveAreaMode\(area\)/);
});
test('speed buttons use a guarded handler and retain stock checks', () => {
  assert.match(html, /function quickAdd\(id\)/);
  assert.match(html, /currentShortcuts\(\)\.favourites\.some/);
  assert.match(html, /function canAdd\(p\)/);
  assert.match(html, /function quickCategory\(category\)/);
});
test('speed keys have explicit draft and publish controls', () => {
  assert.match(html, /function toggleShortcut\(type,value\)/);
  assert.match(html, /function publishShortcuts\(\)/);
  assert.match(html, /function discardShortcuts\(\)/);
  assert.match(html, /shortcutStore\.publish\(area,shortcutStore\.published\(area\)\.version\)/);
});

test('offering module loads before inline app and approval handlers exist',()=>{
  assert.match(html,/src\/offerings\.js/);
  assert.match(html,/BintyOfferings\.createStore\(products\)/);
  assert.match(html,/function stageOffering\(id\)/);
  assert.match(html,/function publishOffering\(id\)/);
  assert.doesNotMatch(html,/function savePrice\(id\)/);
});

test('basket snapshot module loads before inline app',()=>{
  assert.match(html,/src\/basket\.js/);
  assert.match(html,/BintyBasket\.createStore\(\)/);
  assert.match(html,/basketStore\.validatedOrder\(products\)/);
  assert.match(html,/function acceptBasketPrices\(\)/);
});
