'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const html = fs.readFileSync(path.join(root, 'index.html'), 'utf8');

test('demo loads shared catalogue before application script', () => {
  assert.match(html, /<script src="\.\/src\/catalog\.js"><\/script>\s*<script>/);
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
