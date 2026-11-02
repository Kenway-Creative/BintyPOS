'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const { createStore, areaMode } = require('../src/keyboards.js');
const vendors = ['Pattersons', 'Spuddy Hell', 'Lily’s Lounge'];
function store() { return createStore({ 'Main Bar': 'All', 'Food Till': ['Pattersons', 'Spuddy Hell'], 'Theatre': 'Short Menu' }, { vendors }); }
test('legacy all, selected outlets and short profiles normalise', () => {
  const k = store();
  assert.deepEqual(k.areas(), ['Main Bar', 'Food Till', 'Theatre']);
  assert.equal(areaMode(k.published('Main Bar')), 'All');
  assert.deepEqual(areaMode(k.published('Food Till')), ['Pattersons', 'Spuddy Hell']);
  assert.equal(areaMode(k.published('Theatre')), 'Short Menu');
});
test('new profile is a draft until explicit publish', () => {
  const k = store();
  k.stage('Main Bar', { kind: 'vendors', vendors: ['Pattersons'] });
  assert.equal(areaMode(k.published('Main Bar')), 'All');
  assert.deepEqual(areaMode(k.draft('Main Bar')), ['Pattersons']);
});
test('publish increments version, clears draft and records history', () => {
  const k = store();
  k.stage('Main Bar', { kind: 'vendors', vendors: ['Pattersons', 'Spuddy Hell'] });
  assert.equal(k.publish('Main Bar', 1).version, 2);
  assert.equal(k.draft('Main Bar'), null);
  assert.deepEqual(areaMode(k.published('Main Bar')), ['Pattersons', 'Spuddy Hell']);
  assert.equal(k.history().length, 1);
});
test('publish refuses missing or stale version', () => {
  const k = store();
  k.stage('Main Bar', { kind: 'short' });
  assert.throws(() => k.publish('Main Bar'), /KEYBOARD_VERSION_CONFLICT/);
  assert.throws(() => k.publish('Main Bar', 2), /KEYBOARD_VERSION_CONFLICT/);
  assert.equal(k.published('Main Bar').version, 1);
});
test('publish refuses absent draft', () => assert.throws(() => store().publish('Main Bar', 1), /NO_PENDING_DRAFT/));
test('discard leaves published profile untouched', () => {
  const k = store();
  k.stage('Main Bar', { kind: 'short' });
  k.discard('Main Bar');
  assert.equal(k.draft('Main Bar'), null);
  assert.equal(areaMode(k.published('Main Bar')), 'All');
});
test('reject empty, unknown, duplicate and invalid outlet selections', () => {
  const k = store();
  assert.throws(() => k.stage('Main Bar', { kind: 'vendors', vendors: [] }), /EMPTY_OUTLET_SELECTION/);
  assert.throws(() => k.stage('Main Bar', { kind: 'vendors', vendors: ['Unknown'] }), /UNKNOWN_OUTLET/);
  assert.throws(() => k.stage('Main Bar', { kind: 'vendors', vendors: ['Pattersons', 'Pattersons'] }), /DUPLICATE_OUTLET/);
  assert.throws(() => k.stage('Main Bar', { kind: 'short', vendors: ['Pattersons'] }), /UNEXPECTED_VENDORS/);
});
test('reject unknown area for reads and writes', () => {
  const k = store();
  assert.throws(() => k.published('Other'), /UNKNOWN_AREA/);
  assert.throws(() => k.stage('Other', 'All'), /UNKNOWN_AREA/);
});
test('returned published/draft/history snapshots cannot mutate store', () => {
  const k = store();
  k.stage('Main Bar', { kind: 'vendors', vendors: ['Pattersons'] });
  k.draft('Main Bar').vendors.push('Spuddy Hell');
  assert.deepEqual(k.draft('Main Bar').vendors, ['Pattersons']);
  k.publish('Main Bar', 1);
  k.published('Main Bar').vendors.push('Spuddy Hell');
  k.history()[0].vendors.push('Spuddy Hell');
  assert.deepEqual(k.published('Main Bar').vendors, ['Pattersons']);
  assert.deepEqual(k.history()[0].vendors, ['Pattersons']);
});
test('drafts in one area cannot change another area', () => {
  const k = store();
  k.stage('Main Bar', { kind: 'vendors', vendors: ['Lily’s Lounge'] });
  assert.deepEqual(areaMode(k.published('Food Till')), ['Pattersons', 'Spuddy Hell']);
});
test('switching from selected outlets to all or short clears outlet list', () => {
  const k = store();
  k.stage('Food Till', { kind: 'all' });
  assert.deepEqual(k.draft('Food Till').vendors, []);
  k.publish('Food Till', 1);
  k.stage('Food Till', { kind: 'short' });
  assert.deepEqual(k.draft('Food Till').vendors, []);
});
