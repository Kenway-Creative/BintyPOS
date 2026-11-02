'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const {createStore,toMinor}=require('../src/basket.js');
const product=(id='burger',price=12.5,version=1)=>({id,vendor:'Pattersons',name:'Burger',price,version,available:true});
test('captures GBP pence and product revision when first added',()=>{
  const b=createStore();b.add(product());
  assert.deepEqual(b.snapshot().lines[0],{productId:'burger',productVersion:1,vendor:'Pattersons',name:'Burger',unitPriceMinor:1250,quantity:1});
});
test('quantity increments without repricing existing line',()=>{
  const b=createStore();b.add(product());b.add(product('burger',14,2));
  assert.equal(b.snapshot().subtotalMinor,2500);assert.equal(b.quantity('burger'),2);
});
test('catalogue update cannot silently change displayed basket total',()=>{
  const b=createStore();b.add(product());const current=[product('burger',14,2)];
  assert.equal(b.snapshot().subtotalMinor,1250);
  assert.equal(b.review(current).conflicts[0].code,'CATALOGUE_CHANGED');
  assert.equal(b.snapshot().subtotalMinor,1250);
});
test('checkout refuses changed catalogue without explicit acceptance',()=>{
  const b=createStore();b.add(product());
  assert.throws(()=>b.validatedOrder([product('burger',14,2)]),/BASKET_REVIEW_REQUIRED/);
});
test('accepting updated published price reprices explicitly',()=>{
  const b=createStore();b.add(product());
  b.acceptPublished([product('burger',14,2)]);
  assert.equal(b.validatedOrder([product('burger',14,2)]).subtotalMinor,1400);
  assert.equal(b.snapshot().lines[0].productVersion,2);
});
test('availability withdrawal blocks checkout and acceptance',()=>{
  const b=createStore();b.add(product());
  const unavailable={...product(),available:false};
  assert.equal(b.review([unavailable]).conflicts[0].code,'PRODUCT_UNAVAILABLE');
  assert.throws(()=>b.validatedOrder([unavailable]),/BASKET_REVIEW_REQUIRED/);
  assert.throws(()=>b.acceptPublished([unavailable]),/BASKET_UNAVAILABLE/);
});
test('deleted product blocks checkout and acceptance',()=>{
  const b=createStore();b.add(product());
  assert.equal(b.review([]).conflicts[0].code,'PRODUCT_REMOVED');
  assert.throws(()=>b.acceptPublished([]),/BASKET_UNAVAILABLE/);
});
test('unchanged published version validates and returns defensive order copy',()=>{
  const b=createStore();b.add(product());const order=b.validatedOrder([product()]);
  order.lines[0].unitPriceMinor=0;
  assert.equal(b.snapshot().subtotalMinor,1250);
});
test('removing quantity and clearing empty basket are consistent',()=>{
  const b=createStore();b.add(product());b.add(product());b.remove('burger');
  assert.equal(b.snapshot().subtotalMinor,1250);b.remove('burger');
  assert.equal(b.snapshot().subtotalMinor,0);assert.throws(()=>b.validatedOrder([]),/EMPTY_BASKET/);
});
test('invalid fractional or negative prices are rejected',()=>{
  assert.throws(()=>toMinor(1.005),/INVALID_PRICE/);
  assert.throws(()=>toMinor(-1),/INVALID_PRICE/);
  assert.equal(toMinor(9.99),999);
});
test('rejects unavailable additions and invalid product revisions',()=>{
  const b=createStore();assert.throws(()=>b.add({...product(),available:false}),/PRODUCT_UNAVAILABLE/);
  assert.throws(()=>b.add({...product(),version:0}),/INVALID_PRODUCT/);
});
test('multiple vendors preserve their individual ownership and totals',()=>{
  const b=createStore();b.add(product());
  b.add({id:'potato',vendor:'Spuddy Hell',name:'Spud',price:9,version:3});
  const result=b.validatedOrder([product(),{id:'potato',vendor:'Spuddy Hell',name:'Spud',price:9,version:3}]);
  assert.equal(result.subtotalMinor,2150);
  assert.deepEqual(result.lines.map(x=>x.vendor),['Pattersons','Spuddy Hell']);
});
