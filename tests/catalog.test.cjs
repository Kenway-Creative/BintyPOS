'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const catalog = require('../src/catalog.js');
const items = [
  { id: 'burger', vendor: 'Pattersons', category: 'Food', name: 'Burger' },
  { id: 'potato', vendor: 'Spuddy Hell', category: 'Food', name: 'Loaded Potato' },
  { id: 'corona', vendor: 'Lily’s Lounge', category: 'Drink', name: 'Corona' },
  { id: 'cake', vendor: 'Cherry On Top', category: 'Dessert', name: 'Cake' }
];
test('all-area catalogue includes every vendor', () => assert.equal(catalog.project(items).length, 4));
test('single-vendor area is restricted', () => assert.deepEqual(catalog.project(items, { areaMode: 'Pattersons' }).map(x => x.id), ['burger']));
test('multi-vendor area works', () => assert.equal(catalog.project(items, { areaMode: ['Pattersons', 'Spuddy Hell'] }).length, 2));
test('staff folder shows only its outlet', () => assert.deepEqual(catalog.project(items, { outlet: 'Spuddy Hell', channel: 'staff' }).map(x => x.id), ['potato']));
test('guest ignores staff-only folder', () => assert.equal(catalog.project(items, { outlet: 'Spuddy Hell', channel: 'guest' }).length, 4));
test('guest still respects area restrictions', () => assert.equal(catalog.project(items, { areaMode: 'Pattersons', outlet: 'Spuddy Hell', channel: 'guest' }).length, 1));
test('search and category combine', () => assert.deepEqual(catalog.project(items, { category: 'Food', search: ' loaded ' }).map(x => x.id), ['potato']));
test('category tabs reflect current folder', () => assert.deepEqual(catalog.categories(items, { outlet: 'Lily’s Lounge' }), ['Drink']));
test('only allowed outlet shortcuts are shown', () => assert.deepEqual(catalog.outlets(items, ['Pattersons', 'Spuddy Hell']), ['Pattersons', 'Spuddy Hell']));
test('short menu excludes unlisted products', () => assert.deepEqual(catalog.project(items, { areaMode: 'Short Menu' }).map(x => x.id), ['burger', 'corona', 'cake']));
test('unknown area fails closed', () => assert.deepEqual(catalog.project(items, { areaMode: 'Unknown' }), []));
test('catalogue projection does not mutate products', () => { catalog.project(items, { search: 'Burger' }); assert.equal(items[0].name, 'Burger'); });
