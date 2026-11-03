'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const spec=fs.readFileSync(path.join(__dirname,'..','openapi.yaml'),'utf8');
test('quote API documents server-priced validation and explicit acceptance',()=>{
  assert.match(spec,/version: 0\.2\.21/);
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

test('advisory shared ingredient preflight is documented, not a stock reservation',()=>{
  assert.match(spec,/\/venues\/\{venueId\}\/inventory\/preflight:/);
  assert.match(spec,/operationId: preflightInventory/);
  assert.match(spec,/InventoryPreflight:/);
  assert.match(spec,/stockRevision:/);
  assert.match(spec,/NOT a reservation/);
});

test('virtual stockroom API separates logical category from physical counting locations',()=>{
 assert.match(spec,/operationId: listVirtualStockrooms/);
 assert.match(spec,/operationId: submitPhysicalStockCount/);
 assert.match(spec,/operationId: reassignIngredientStockroom/);
 assert.match(spec,/PhysicalCountInput:/);
 assert.match(spec,/locationId: \{type: string, description: Real physical counting location/);
});

test('reservation API uses accepted quotes, idempotency and service-only commit',()=>{
 assert.match(spec,/operationId: reserveInventoryForQuote/);
 assert.match(spec,/operationId: getInventoryReservation/);
 assert.match(spec,/operationId: releaseInventoryReservation/);
 assert.match(spec,/operationId: commitInventoryReservation/);
 assert.match(spec,/ReservationRecord:/);
 assert.match(spec,/security: \[\{serviceAuth: \[\]\}\]/);
});

test('proposed order lifecycle is explicitly read-only and mock payment remains internal',()=>{
 assert.match(spec,/operationId: getOrderLifecycle/);
 assert.match(spec,/OrderLifecycle:/);
 assert.match(spec,/MOCK authorisation only/);
});

test('v0.2.22 proposed checkout auth requires bearer scope without exposing mock payment',()=>{
 assert.match(spec,/version: 0\.2\.21/);
 assert.match(spec,/operationId: createBasketQuote\n      security: \[\{checkoutAuth: \[\]\}\]/);
 assert.match(spec,/operationId: submitOrder\n      security: \[\{checkoutAuth: \[\]\}\]/);
 assert.match(spec,/NO HTTP authentication/);
});
