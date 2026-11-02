'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const {createStore}=require('../src/reservations.js');
function setup(initial={vodka:10,ice:6}){
 let stock={...initial},time=10000,consumeCalls=0;
 const s=createStore({readStock:()=>({...stock}),consumeStock:d=>{
  for(const [id,q] of Object.entries(d))if(q>(stock[id]??0))throw Error('ADAPTER_STOCK_CONFLICT');
  for(const [id,q] of Object.entries(d))stock[id]-=q;
  consumeCalls++;return {movements:Object.entries(d).map(([ingredientId,quantity])=>({ingredientId,quantity}))};
 },now:()=>time});
 return {s,stock:()=>({...stock}),setStock:v=>stock={...v},advance:ms=>time+=ms,calls:()=>consumeCalls};
}
test('holds reduce reservable stock but do not physically deduct',()=>{const x=setup();x.s.reserve({key:'order-1',demands:{vodka:7}});assert.equal(x.stock().vodka,10);assert.equal(x.s.available().vodka,3);assert.equal(x.s.activeCount(),1)});
test('second till cannot reserve already held stock',()=>{const x=setup();x.s.reserve({key:'a',demands:{vodka:7}});assert.throws(()=>x.s.reserve({key:'b',demands:{vodka:4}}),e=>e.message==='INSUFFICIENT_RESERVABLE_STOCK'&&e.shortages[0].available===3)});
test('different ingredients reserve together or not at all',()=>{const x=setup();assert.throws(()=>x.s.reserve({key:'a',demands:{vodka:3,ice:7}}),/INSUFFICIENT_RESERVABLE_STOCK/);assert.equal(x.s.available().vodka,10)});
test('commit deducts exactly once with duplicate idempotent retry',()=>{const x=setup();x.s.reserve({key:'a',demands:{vodka:3,ice:2}});assert.equal(x.s.commit('a').status,'committed');assert.equal(x.s.commit('a').status,'committed');assert.deepEqual(x.stock(),{vodka:7,ice:4});assert.equal(x.calls(),1)});
test('same key and equivalent demand is an idempotent reservation retry',()=>{const x=setup();const a=x.s.reserve({key:'a',demands:{vodka:2,ice:1}});const b=x.s.reserve({key:'a',demands:{ice:1,vodka:2}});assert.deepEqual(a,b);assert.equal(x.s.activeCount(),1)});
test('same key different demand is rejected even after commit',()=>{const x=setup();x.s.reserve({key:'a',demands:{vodka:2}});x.s.commit('a');assert.throws(()=>x.s.reserve({key:'a',demands:{vodka:3}}),/IDEMPOTENCY_CONFLICT/)});
test('release restores availability and is idempotent',()=>{const x=setup();x.s.reserve({key:'a',demands:{vodka:9}});assert.equal(x.s.release('a').status,'released');assert.equal(x.s.release('a').status,'released');assert.equal(x.s.available().vodka,10);assert.throws(()=>x.s.commit('a'),/RESERVATION_NOT_ACTIVE/)});
test('expiry restores availability and cannot be revived by same key',()=>{const x=setup();x.s.reserve({key:'a',demands:{vodka:9},ttlMs:1000});x.advance(1000);assert.equal(x.s.status('a').status,'expired');assert.equal(x.s.available().vodka,10);assert.equal(x.s.reserve({key:'a',demands:{vodka:9}}).status,'expired');assert.throws(()=>x.s.commit('a'),/RESERVATION_NOT_ACTIVE/)});
test('external count decrease fails closed and releases conflicted hold',()=>{const x=setup();x.s.reserve({key:'a',demands:{vodka:7}});x.setStock({vodka:4,ice:6});assert.throws(()=>x.s.commit('a'),/RESERVATION_STOCK_CONFLICT/);assert.equal(x.s.status('a').status,'conflicted');assert.equal(x.calls(),0);assert.equal(x.s.available().vodka,4)});
test('adapter exception retains hold without claiming success',()=>{let n=0;const s=createStore({readStock:()=>({vodka:5}),consumeStock:()=>{n++;throw Error('DB_UNAVAILABLE')}});s.reserve({key:'a',demands:{vodka:2}});assert.throws(()=>s.commit('a'),/DB_UNAVAILABLE/);assert.equal(s.status('a').status,'held');assert.equal(n,1)});
test('committed reservation cannot be released',()=>{const x=setup();x.s.reserve({key:'a',demands:{vodka:1}});x.s.commit('a');assert.throws(()=>x.s.release('a'),/RESERVATION_ALREADY_COMMITTED/)});
test('empty recipe demand supports untracked products',()=>{const x=setup();x.s.reserve({key:'a',demands:{}});x.s.commit('a');assert.deepEqual(x.stock(),{vodka:10,ice:6})});
test('input validation rejects negative, fractional, unknown and overflow quantities',()=>{const x=setup();for(const v of [-1,0,1.2,Number.MAX_SAFE_INTEGER+1])assert.throws(()=>x.s.reserve({key:'a',demands:{vodka:v}}),/INVALID_RESERVATION_DEMAND/);assert.throws(()=>x.s.reserve({key:'a',demands:{['__proto__']:1}}),/INVALID_RESERVATION_DEMAND/);assert.throws(()=>x.s.reserve({key:'',demands:{}}),/INVALID_IDEMPOTENCY_KEY/)});
test('invalid TTL and clock fail closed',()=>{const x=setup();assert.throws(()=>x.s.reserve({key:'a',demands:{},ttlMs:0}),/INVALID_RESERVATION_TTL/);assert.throws(()=>createStore({readStock:()=>({}),consumeStock:()=>{},now:()=>-1}).reserve({key:'a',demands:{}}),/INVALID_RESERVATION_CLOCK/)});
test('returned records are defensive snapshots',()=>{const x=setup();const a=x.s.reserve({key:'a',demands:{vodka:2}});a.demands.vodka=1000;const b=x.s.status('a');b.status='committed';assert.equal(x.s.status('a').demands.vodka,2);assert.equal(x.s.status('a').status,'held')});
test('unknown reservation and malformed stock fail closed',()=>{const x=setup();assert.throws(()=>x.s.commit('missing'),/UNKNOWN_RESERVATION/);assert.throws(()=>createStore({readStock:()=>({vodka:-1}),consumeStock:()=>{}}).reserve({key:'a',demands:{vodka:1}}),/INVALID_RESERVATION_STOCK/)});
