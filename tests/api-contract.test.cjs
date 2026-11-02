'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const spec=fs.readFileSync(path.join(__dirname,'..','openapi.yaml'),'utf8');
test('quote API documents server-priced validation and explicit acceptance',()=>{
  assert.match(spec,/version: 0\.2\.5/);
  assert.match(spec,/\/venues\/\{venueId\}\/quotes:/);
  assert.match(spec,/operationId: createBasketQuote/);
  assert.match(spec,/\/venues\/\{venueId\}\/quotes\/\{quoteId\}\/accept-prices:/);
  assert.match(spec,/operationId: acceptBasketQuotePrices/);
});
test('order submission requires an authoritative quote reference',()=>{
  assert.match(spec,/required: \[areaId, quoteId, quoteRevision\]/);
  assert.match(spec,/name: Idempotency-Key/);
});
test('snapshot contract uses integer minor units and version checks',()=>{
  assert.match(spec,/BasketLineSnapshot:/);
  assert.match(spec,/unitPriceMinor: \{type: integer, minimum: 0/);
  assert.match(spec,/productVersion: \{type: integer, minimum: 1/);
  assert.match(spec,/CATALOGUE_CHANGED, PRODUCT_UNAVAILABLE, PRODUCT_REMOVED/);
});
