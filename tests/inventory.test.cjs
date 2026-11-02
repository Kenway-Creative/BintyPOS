'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const {preflight,consume}=require('../src/inventory.js');
const products=[
 {id:'corona',vendor:'Lily',recipe:{corona:1}},
 {id:'bucket',vendor:'Lily',recipe:{corona:5}},
 {id:'party',vendor:'Other',recipe:{corona:2,ice:1}},
 {id:'burger',vendor:'Pattersons',recipe:{}}
];
const line=(productId,quantity=1)=>({productId,quantity});
test('aggregates ingredient demand across products and vendors',()=>{
 const r=preflight([line('corona',2),line('party',2)],products,{corona:6,ice:2});
 assert.equal(r.ok,true);assert.deepEqual(r.demands,{corona:6,ice:2});
});
test('blocks combined demand even when each product separately fits',()=>{
 const r=preflight([line('corona',4),line('bucket')],products,{corona:8});
 assert.equal(r.ok,false);assert.deepEqual(r.shortages,[{ingredientId:'corona',required:9,available:8}]);
});
test('missing ingredient stock is zero',()=>{
 const r=preflight([line('party')],products,{corona:3});
 assert.deepEqual(r.shortages,[{ingredientId:'ice',required:1,available:0}]);
});
test('empty recipes are valid and do not consume stock',()=>{
 const stock={corona:8};const result=consume([line('burger',2)],products,stock);
 assert.deepEqual(result.stock,stock);assert.notStrictEqual(result.stock,stock);
});
test('successful consume returns new stock without mutating input',()=>{
 const stock={corona:8,ice:2};const result=consume([line('corona',3),line('party')],products,stock);
 assert.deepEqual(result.stock,{corona:3,ice:1});assert.deepEqual(stock,{corona:8,ice:2});
});
test('insufficient consume throws and never mutates input',()=>{
 const stock={corona:8,ice:2};assert.throws(()=>consume([line('corona',4),line('bucket')],products,stock),/INSUFFICIENT_SHARED_STOCK/);
 assert.deepEqual(stock,{corona:8,ice:2});
});
test('rejects unavailable or unknown products',()=>{
 assert.throws(()=>preflight([line('unknown')],products,{}),/PRODUCT_UNAVAILABLE/);
 assert.throws(()=>preflight([line('corona')],[{...products[0],available:false}],{corona:3}),/PRODUCT_UNAVAILABLE/);
});
test('rejects invalid quantities and malformed recipes',()=>{
 assert.throws(()=>preflight([line('corona',-1)],products,{}),/INVALID_ORDER_LINE/);
 assert.throws(()=>preflight([line('corona',0.5)],products,{}),/INVALID_ORDER_LINE/);
 assert.throws(()=>preflight([line('corona')],[{id:'corona',recipe:{corona:0}}],{}),/INVALID_RECIPE/);
 assert.throws(()=>preflight([line('corona')],[{id:'corona',recipe:null}],{}),/INVALID_RECIPE/);
});
test('rejects invalid stock and overflow',()=>{
 assert.throws(()=>preflight([],products,{corona:-1}),/INVALID_STOCK/);
 assert.throws(()=>preflight([],products,{corona:1.5}),/INVALID_STOCK/);
 assert.throws(()=>preflight([line('corona',Number.MAX_SAFE_INTEGER),line('corona')],products,{corona:0}),/INVENTORY_OVERFLOW/);
});
test('preflight is deterministic and does not mutate inputs',()=>{
 const stock={corona:10};const lines=[line('corona',2)];const first=preflight(lines,products,stock);
 first.demands.corona=999;assert.equal(preflight(lines,products,stock).demands.corona,2);
 assert.deepEqual(stock,{corona:10});assert.deepEqual(lines,[line('corona',2)]);
});
