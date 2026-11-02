'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const {createStore}=require('../src/stockrooms.js');
const model=()=>createStore({
 rooms:[{id:'communal',name:'Communal spirits'},{id:'cellar',name:'Cellar'}],
 locations:[{id:'bar',name:'Main Bar'},{id:'lounge',name:'Lounge'},{id:'cellar',name:'Cellar'}],
 items:[
  {id:'vodka',roomId:'communal',counts:{bar:4,lounge:6}},
  {id:'lager',roomId:'cellar',counts:{cellar:12}}
 ]
});
test('logical room totals sum all physical count locations exactly once',()=>{const s=model();assert.deepEqual(s.totals(),{vodka:10,lager:12});assert.equal(s.countSheet('communal')[0].locations.length,3)});
test('different physical locations remain separate',()=>{const s=model();assert.deepEqual(s.countSheet('communal')[0].locations.map(x=>x.quantity),[4,6,0])});
test('a physical count changes shared total',()=>{const s=model();s.setCount('vodka','lounge',3);assert.equal(s.totals().vodka,7)});
test('moving an ingredient category preserves counts and total',()=>{const s=model();s.moveRoom('vodka','cellar');assert.equal(s.countSheet('communal').length,0);assert.equal(s.countSheet('cellar').length,2);assert.equal(s.totals().vodka,10)});
test('consumption spans physical locations and is deterministic',()=>{const s=model();const r=s.consume({vodka:7});assert.deepEqual(r.movements,[{ingredientId:'vodka',roomId:'communal',locationId:'bar',quantity:4},{ingredientId:'vodka',roomId:'communal',locationId:'lounge',quantity:3}]);assert.equal(s.totals().vodka,3)});
test('shortage fails atomically across ingredients',()=>{const s=model();assert.throws(()=>s.consume({vodka:2,lager:13}),/INSUFFICIENT_SHARED_STOCK/);assert.deepEqual(s.totals(),{vodka:10,lager:12})});
test('unknown ingredient cannot be silently consumed',()=>{assert.throws(()=>model().consume({sugar:1}),/UNKNOWN_INGREDIENT/)});
test('invalid counts and negative demand fail closed',()=>{const s=model();assert.throws(()=>s.setCount('vodka','bar',-1),/INVALID_LOCATION_COUNT/);assert.throws(()=>s.consume({vodka:0}),/INVALID_STOCKROOM_DEMAND/)});
test('unknown count location and room fail closed',()=>{const s=model();assert.throws(()=>s.setCount('vodka','bogus',1),/INVALID_LOCATION_COUNT/);assert.throws(()=>s.moveRoom('vodka','bogus'),/UNKNOWN_STOCKROOM/)});
test('snapshots and count sheets are defensive',()=>{const s=model();const snapshot=s.snapshot();snapshot.items[0].counts.bar=900;const sheet=s.countSheet('communal');sheet[0].locations[0].quantity=900;assert.equal(s.totals().vodka,10)});
test('rejects duplicate item and duplicate room IDs',()=>{const v=model().snapshot();v.items.push(v.items[0]);assert.throws(()=>createStore(v),/INVALID_STOCKROOM_ITEM/);v.items.pop();v.rooms.push(v.rooms[0]);assert.throws(()=>createStore(v),/INVALID_STOCKROOM_ID/)});
test('rejects unknown physical location and overflowing totals',()=>{const v=model().snapshot();v.items[0].counts.other=1;assert.throws(()=>createStore(v),/INVALID_LOCATION_COUNT/);delete v.items[0].counts.other;v.items[0].counts.bar=Number.MAX_SAFE_INTEGER;assert.throws(()=>createStore(v),/STOCKROOM_OVERFLOW/)});
