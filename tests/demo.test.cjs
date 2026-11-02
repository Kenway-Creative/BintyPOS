'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const html = fs.readFileSync(path.join(root, 'index.html'), 'utf8');

test('demo loads shared catalogue before application script', () => {
  assert.match(html, /<script src="\.\/src\/catalog\.js"><\/script>\s*<script src="\.\/src\/keyboards\.js"><\/script>\s*<script>/);
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
  assert.match(html, /<script src="\.\/src\/catalog\.js"><\/script>\s*<script src="\.\/src\/keyboards\.js"><\/script>\s*<script>/);
});
test('till and QR use only published keyboard profiles', () => {
  assert.match(html, /BintyKeyboards\.areaMode\(keyboardStore\.published\(areaId\)\)/);
  assert.match(html, /function publishKeyboard\(\)/);
  assert.match(html, /keyboardStore\.publish\(area,keyboardStore\.published\(area\)\.version\)/);
  assert.match(html, /function discardKeyboard\(\)/);
});
