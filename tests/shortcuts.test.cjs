'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const catalog = require('../src/catalog.js');
const { createStore, normalise, visible, MAX_FAVOURITES, MAX_CATEGORIES } = require('../src/shortcuts.js');
const products = [
  { id: 'burger', name: 'Burger', vendor: 'Pattersons', category: 'Food' },
  { id: 'potato', name: 'Spud', vendor: 'Spuddy Hell', category: 'Food' },
  { id: 'corona', name: 'Corona', vendor: 'Lily’s Lounge', category: 'Packaged' },
  { id: 'cake', name: 'Cake', vendor: 'Cherry On Top', category: 'Desserts' }
];
function store() {
  return createStore({ 'Main Bar': { productIds: ['corona', 'burger', 'potato'], categories: ['Food', 'Packaged'] } }, { areas: ['Main Bar', 'Theatre'], products });
}
test('per-area initial favourites and categories are ordered', () => {
  const s = store();
  assert.deepEqual(s.published('Main Bar').productIds, ['corona', 'burger', 'potato']);
  assert.deepEqual(s.published('Main Bar').categories, ['Food', 'Packaged']);
  assert.deepEqual(s.published('Theatre').productIds, []);
});
test('draft is not visible on published till until publish', () => {
  const s = store();
  s.stage('Main Bar', { productIds: ['cake'], categories: ['Desserts'] });
  assert.deepEqual(s.published('Main Bar').productIds, ['corona', 'burger', 'potato']);
  assert.deepEqual(s.draft('Main Bar').productIds, ['cake']);
});
test('publish increments version, saves history and clears draft', () => {
  const s = store();
  s.stage('Main Bar', { productIds: ['cake'], categories: [] });
  assert.equal(s.publish('Main Bar', 1).version, 2);
  assert.deepEqual(s.published('Main Bar').productIds, ['cake']);
  assert.equal(s.draft('Main Bar'), null);
  assert.equal(s.history().length, 1);
});
test('stale publish and missing draft fail closed', () => {
  const s = store();
  assert.throws(() => s.publish('Main Bar', 1), /NO_PENDING_DRAFT/);
  s.stage('Main Bar', { productIds: [], categories: [] });
  assert.throws(() => s.publish('Main Bar', 2), /SHORTCUT_VERSION_CONFLICT/);
  assert.equal(s.published('Main Bar').version, 1);
});
test('discard leaves live shortcuts unchanged', () => {
  const s = store();
  s.stage('Main Bar', { productIds: ['cake'], categories: [] });
  s.discard('Main Bar');
  assert.equal(s.draft('Main Bar'), null);
  assert.equal(s.published('Main Bar').productIds[0], 'corona');
});
test('unknown area rejects reads and writes', () => {
  const s = store();
  assert.throws(() => s.published('Ghost'), /UNKNOWN_AREA/);
  assert.throws(() => s.stage('Ghost', {}), /UNKNOWN_AREA/);
});
test('unknown product, category and duplicate shortcut reject', () => {
  assert.throws(() => normalise({ productIds: ['ghost'] }, products), /UNKNOWN_PRODUCT/);
  assert.throws(() => normalise({ categories: ['Ghost'] }, products), /UNKNOWN_CATEGORY/);
  assert.throws(() => normalise({ productIds: ['burger', 'burger'] }, products), /DUPLICATE_SHORTCUT/);
  assert.throws(() => normalise({ categories: ['Food', 'Food'] }, products), /DUPLICATE_SHORTCUT/);
});
test('favourites and categories have touch-friendly maximums', () => {
  assert.equal(MAX_FAVOURITES, 8);
  assert.equal(MAX_CATEGORIES, 6);
  assert.throws(() => normalise({ productIds: Array(9).fill('burger') }, products), /SHORTCUT_LIMIT/);
  assert.throws(() => normalise({ categories: Array(7).fill('Food') }, products), /SHORTCUT_LIMIT/);
});
test('invalid shortcut shapes reject', () => {
  assert.throws(() => normalise(null, products), /INVALID_SHORTCUTS/);
  assert.throws(() => normalise({ productIds: 'burger' }, products), /INVALID_SHORTCUTS/);
});
test('defensive snapshots prevent accidental mutation', () => {
  const s = store();
  s.published('Main Bar').productIds.push('cake');
  s.stage('Main Bar', { productIds: ['cake'], categories: [] });
  s.draft('Main Bar').productIds.push('burger');
  assert.deepEqual(s.published('Main Bar').productIds, ['corona', 'burger', 'potato']);
  assert.deepEqual(s.draft('Main Bar').productIds, ['cake']);
});
test('a restricted bar keyboard hides forbidden favourite products', () => {
  const s = store();
  const result = visible(products, ['Pattersons'], s.published('Main Bar'), catalog);
  assert.deepEqual(result.favourites.map(p => p.id), ['burger']);
  assert.deepEqual(result.categories, ['Food']);
});
test('published keyboard changes dynamically hide now-inaccessible shortcuts', () => {
  const s = store();
  const before = visible(products, 'All', s.published('Main Bar'), catalog);
  const after = visible(products, ['Spuddy Hell'], s.published('Main Bar'), catalog);
  assert.equal(before.favourites.length, 3);
  assert.deepEqual(after.favourites.map(p => p.id), ['potato']);
});
test('shortcut projection does not mutate products or stored settings', () => {
  const s = store();
  const original = JSON.stringify(products);
  visible(products, 'All', s.published('Main Bar'), catalog);
  assert.equal(JSON.stringify(products), original);
  assert.equal(s.published('Main Bar').version, 1);
});
test('area drafts do not affect other areas', () => {
  const s = store();
  s.stage('Theatre', { productIds: ['cake'], categories: ['Desserts'] });
  assert.deepEqual(s.published('Main Bar').productIds, ['corona', 'burger', 'potato']);
});
