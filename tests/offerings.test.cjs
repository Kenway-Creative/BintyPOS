'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const {createStore,normalisePatch}=require('../src/offerings.js');
const seed=[
 {id:'burger',vendor:'Pattersons',name:'Burger',price:12.5,category:'Food',recipe:{}},
 {id:'potato',vendor:'Spuddy Hell',name:'Spud',price:9,category:'Food',recipe:{}}
];
const venue={id:'binty-demo',role:'venue_admin'};
const pat={id:'pat-demo',role:'outlet_manager',outlet:'Pattersons'};
const spud={id:'spud-demo',role:'outlet_manager',outlet:'Spuddy Hell'};
const store=()=>createStore(seed);
test('initial products are published and independently versioned',()=>{
 const s=store();assert.equal(s.product('burger').version,1);assert.equal(s.product('burger').available,true);
 assert.equal(s.published().length,2);
});
test('outlet manager can stage their own name and availability',()=>{
 const s=store();const d=s.stage('burger',{name:'New Burger',available:false},pat);
 assert.equal(d.outlet,'Pattersons');assert.equal(s.product('burger').name,'Burger');
 assert.equal(s.product('burger').available,true);
});
test('outlet manager cannot change another outlet',()=>{
 const s=store();assert.throws(()=>s.stage('potato',{price:10},pat),/OUTLET_SCOPE_DENIED/);
});
test('outlet manager cannot publish even their own change',()=>{
 const s=store();s.stage('burger',{price:13},pat);
 assert.throws(()=>s.publish('burger',pat,1),/VENUE_APPROVAL_REQUIRED/);
 assert.equal(s.product('burger').price,12.5);
});
test('venue manager approves and publishes price changes',()=>{
 const s=store();s.stage('burger',{price:13.5},pat);
 const p=s.publish('burger',venue,1);assert.equal(p.price,13.5);assert.equal(p.version,2);
 assert.equal(s.draft('burger'),null);assert.equal(s.product('burger').price,13.5);
});
test('reject leaves live price unchanged and logs rejection',()=>{
 const s=store();s.stage('burger',{price:14},pat);s.reject('burger',venue,'Price held');
 assert.equal(s.product('burger').price,12.5);assert.equal(s.pending().length,0);
 assert.equal(s.audit().at(-1).action,'offering.draft_rejected');
});
test('stale publish is rejected without changing published product',()=>{
 const s=store();s.stage('burger',{price:14},pat);
 assert.throws(()=>s.publish('burger',venue,2),/OFFERING_VERSION_CONFLICT/);
 assert.equal(s.product('burger').price,12.5);
});
test('only one pending proposal per product, independent across outlets',()=>{
 const s=store();s.stage('burger',{price:14},pat);
 assert.throws(()=>s.stage('burger',{price:15},venue),/DRAFT_ALREADY_EXISTS/);
 s.stage('potato',{price:10},spud);assert.equal(s.pending().length,2);
});
test('only draft creator or venue manager can discard',()=>{
 const s=store();s.stage('burger',{price:14},pat);
 assert.throws(()=>s.discard('burger',{id:'another',role:'outlet_manager',outlet:'Pattersons'}),/DRAFT_OWNER_REQUIRED/);
 s.discard('burger',pat);assert.equal(s.pending().length,0);
});
test('invalid prices and unapproved fields reject',()=>{
 const s=store();
 for(const v of [-1,Infinity,NaN,12.345,'14'])assert.throws(()=>s.stage('burger',{price:v},pat),/INVALID_PRICE/);
 assert.throws(()=>s.stage('burger',{vendor:'Spuddy Hell'},pat),/INVALID_OFFERING_PATCH/);
 assert.throws(()=>s.stage('burger',{available:'yes'},pat),/INVALID_AVAILABILITY/);
});
test('empty and no-op proposals are rejected',()=>{
 const s=store();assert.throws(()=>s.stage('burger',{},pat),/INVALID_OFFERING_PATCH/);
 assert.throws(()=>s.stage('burger',{price:12.5},pat),/NO_CHANGES/);
});
test('audit log is append-only snapshots and contains actor and version',()=>{
 const s=store();s.stage('burger',{price:13},pat);s.publish('burger',venue,1);
 const history=s.audit();assert.equal(history.length,2);
 assert.equal(history[0].actorId,'pat-demo');assert.equal(history[1].toVersion,2);
 history[0].changes.price=999;assert.equal(s.audit()[0].changes.price,13);
});
test('mutating returned products or drafts does not change live data',()=>{
 const s=store();s.stage('burger',{name:'New Burger'},pat);
 s.product('burger').name='Corrupted';s.draft('burger').changes.name='Corrupted';
 s.published()[0].name='Corrupted';
 assert.equal(s.product('burger').name,'Burger');assert.equal(s.draft('burger').changes.name,'New Burger');
});
test('unknown product and invalid actor fail closed',()=>{
 const s=store();assert.throws(()=>s.stage('ghost',{price:5},venue),/UNKNOWN_PRODUCT/);
 assert.throws(()=>s.stage('burger',{price:13},{role:'venue_admin'}),/INVALID_ACTOR/);
});
test('valid patch preserves product identity and recipe',()=>{
 const s=store();s.stage('burger',{available:false},pat);const p=s.publish('burger',venue,1);
 assert.equal(p.id,'burger');assert.equal(p.vendor,'Pattersons');assert.deepEqual(p.recipe,{});
});
