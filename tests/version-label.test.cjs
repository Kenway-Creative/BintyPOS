'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const html = fs.readFileSync(path.join(__dirname, '..', 'index.html'), 'utf8');

test('visible prototype labels distinguish framework and browser demo versions', () => {
  assert.match(html, /BINTYPOS FRAMEWORK v0\.2\.28 · BROWSER DEMO v0\.2\.8/);
  assert.match(html, /Browser demo v0\.2\.8 \(framework v0\.2\.28\): in-browser state/);
  assert.doesNotMatch(html, /Prototype v0\.2\.8:/);
});

test('demo payment safety disclosure remains visible', () => {
  assert.match(html, /SIMULATED PAYMENTS/);
  assert.match(html, /No multi-device lock, real stock reservations, Dojo/);
});
