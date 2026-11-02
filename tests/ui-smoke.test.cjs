'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const catalog = require('../src/catalog.js');
const keyboards = require('../src/keyboards.js');
const shortcuts = require('../src/shortcuts.js');
const offerings = require('../src/offerings.js');
const basket = require('../src/basket.js');
const inventory = require('../src/inventory.js');
const stockrooms = require('../src/stockrooms.js');
const html = fs.readFileSync(path.join(__dirname, '..', 'index.html'), 'utf8');
const inline = 'const seed=' + html.split('<script>\nconst seed=')[1].split('</script>')[0];

function boot() {
  const nodes = {};
  const context = {
    document: { getElementById: id => nodes[id] || (nodes[id] = { innerHTML: '', value: '' }) },
    window: {},
    structuredClone,
    BintyCatalog: catalog,
    BintyKeyboards: keyboards,
    BintyShortcuts: shortcuts,
    BintyOfferings: offerings,
    BintyBasket: basket,
    BintyInventory: inventory,
    BintyStockrooms: stockrooms
  };
  vm.createContext(context);
  vm.runInContext(inline, context, { timeout: 1000 });
  const run = expression => vm.runInContext(expression, context, { timeout: 1000 });
  return { run, nodes };
}
test('staff till shows published speed keys and one-tap categories', () => {
  const { nodes } = boot();
  assert.match(nodes.app.innerHTML, /Speed keys/);
  assert.match(nodes.app.innerHTML, /★ Corona/);
  assert.match(nodes.app.innerHTML, /Jump to category/);
});
test('one-tap favourite adds to shared basket, preserves order on outlet change', () => {
  const { run } = boot();
  run('quickAdd("corona"); enterFolder("Pattersons"); quickAdd("burger")');
  assert.equal(run('cart.corona'), 1);
  assert.equal(run('cart.burger'), 1);
});
test('category jump resets folder but retains basket', () => {
  const { run } = boot();
  run('quickAdd("burger"); enterFolder("Spuddy Hell"); quickCategory("Food")');
  assert.equal(run('outletFolder'), 'All');
  assert.equal(run('filter'), 'Food');
  assert.equal(run('cart.burger'), 1);
});
test('guest QR has no staff speed-key panel', () => {
  const { run, nodes } = boot();
  run('setTab("qr")');
  assert.doesNotMatch(nodes.app.innerHTML, /aria-label="Speed shortcuts"/);
  assert.match(nodes.app.innerHTML, /Guest QR ordering/);
});
test('restricted area hides disallowed favourite and refuses direct add', () => {
  const { run, nodes } = boot();
  run('setArea("Pattersons")');
  assert.doesNotMatch(nodes.app.innerHTML, /★ Corona/);
  run('quickAdd("corona")');
  assert.equal(run('cart.corona'), undefined);
});
test('draft changes do not show on till before publication', () => {
  const { run, nodes } = boot();
  run('setTab("backoffice")');
  nodes.demoPin = { value: '2468' };
  run('unlockDemo(); toggleShortcut("productIds","cake"); setTab("till")');
  assert.doesNotMatch(nodes.app.innerHTML, /★ Cherry On Top Cake/);
  assert.equal(run('shortcutStore.published("Main Bar").version'), 1);
});
test('published shortcut becomes available without changing existing basket', () => {
  const { run, nodes } = boot();
  run('quickAdd("corona"); setTab("backoffice")');
  nodes.demoPin = { value: '2468' };
  run('unlockDemo(); toggleShortcut("productIds","cake"); publishShortcuts(); setTab("till")');
  assert.match(nodes.app.innerHTML, /★ Cherry On Top Cake/);
  assert.equal(run('shortcutStore.published("Main Bar").version'), 2);
  assert.equal(run('cart.corona'), 1);
});
test('out-of-stock speed key is disabled and cannot add more', () => {
  const { run, nodes } = boot();
  run('demoSetStock("corona",0); render()');
  assert.match(nodes.app.innerHTML, /class="speed-key" disabled/);
  run('quickAdd("corona")');
  assert.equal(run('cart.corona'), undefined);
});

test('outlet proposal stays invisible until venue approval',()=>{
 const {run,nodes}=boot();
 run('setTab("backoffice")');nodes.demoPin={value:'1357'};run('unlockDemo()');
 nodes.offerName={value:'Pattersons Burger'};nodes.offerPrice={value:'14.00'};nodes.offerAvailable={checked:true};
 run('stageOffering("burger")');
 assert.equal(run('offeringStore.pending().length'),1);
 assert.equal(run('products.find(p=>p.id==="burger").price'),12.5);
 run('setTab("qr")');assert.match(nodes.app.innerHTML,/£12\.50/);
});
test('venue approval publishes to shared staff and QR catalogue',()=>{
 const {run,nodes}=boot();
 run('setTab("backoffice")');nodes.demoPin={value:'1357'};run('unlockDemo()');
 nodes.offerName={value:'Pattersons Burger'};nodes.offerPrice={value:'14.00'};nodes.offerAvailable={checked:true};
 run('stageOffering("burger");setTab("backoffice")');nodes.demoPin={value:'2468'};run('unlockDemo()');
 assert.match(nodes.app.innerHTML,/Venue approval queue \(1\)/);
 run('publishOffering("burger");setTab("qr")');
 assert.equal(run('products.find(p=>p.id==="burger").price'),14);
 assert.match(nodes.app.innerHTML,/£14\.00/);
});
test('venue rejection keeps published offering and availability',()=>{
 const {run,nodes}=boot();
 run('setTab("backoffice")');nodes.demoPin={value:'1357'};run('unlockDemo()');
 nodes.offerName={value:'Pattersons Burger'};nodes.offerPrice={value:'12.50'};nodes.offerAvailable={checked:false};
 run('stageOffering("burger");setTab("backoffice")');nodes.demoPin={value:'2468'};run('unlockDemo();rejectOffering("burger");setTab("till")');
 assert.equal(run('products.find(p=>p.id==="burger").available'),true);
 assert.equal(run('offeringStore.pending().length'),0);
});
test('approved unavailability blocks till and QR additions',()=>{
 const {run,nodes}=boot();
 run('setTab("backoffice")');nodes.demoPin={value:'1357'};run('unlockDemo()');
 nodes.offerName={value:'Pattersons Burger'};nodes.offerPrice={value:'12.50'};nodes.offerAvailable={checked:false};
 run('stageOffering("burger");setTab("backoffice")');nodes.demoPin={value:'2468'};run('unlockDemo();publishOffering("burger")');
 assert.equal(run('canAdd(products.find(p=>p.id==="burger"))'),false);
 run('setTab("qr")');assert.match(nodes.app.innerHTML,/Pattersons Burger/);
});

test('published price change keeps original basket total until explicit acceptance',()=>{
 const {run,nodes}=boot();
 run('add("burger");setTab("backoffice")');nodes.demoPin={value:'1357'};run('unlockDemo()');
 nodes.offerName={value:'Pattersons Burger'};nodes.offerPrice={value:'14.00'};nodes.offerAvailable={checked:true};
 run('stageOffering("burger");setTab("backoffice")');nodes.demoPin={value:'2468'};run('unlockDemo();publishOffering("burger");setTab("till")');
 assert.equal(run('total()'),12.5);
 assert.match(nodes.app.innerHTML,/Basket review required/);
 run('checkout()');
 assert.equal(run('orders.length'),0);
 assert.match(nodes.app.innerHTML,/Checkout blocked/);
});
test('accepting changed published price allows simulated checkout with new total',()=>{
 const {run,nodes}=boot();
 run('add("burger");setTab("backoffice")');nodes.demoPin={value:'1357'};run('unlockDemo()');
 nodes.offerName={value:'Pattersons Burger'};nodes.offerPrice={value:'14.00'};nodes.offerAvailable={checked:true};
 run('stageOffering("burger");setTab("backoffice")');nodes.demoPin={value:'2468'};run('unlockDemo();publishOffering("burger");setTab("till")');
 run('acceptBasketPrices()');
 assert.equal(run('total()'),14);
 run('checkout()');
 assert.equal(run('orders.length'),1);
 assert.equal(run('orders[0].total'),14);
});
test('published unavailability blocks checkout and price acceptance',()=>{
 const {run,nodes}=boot();
 run('add("burger");setTab("backoffice")');nodes.demoPin={value:'1357'};run('unlockDemo()');
 nodes.offerName={value:'Pattersons Burger'};nodes.offerPrice={value:'12.50'};nodes.offerAvailable={checked:false};
 run('stageOffering("burger");setTab("backoffice")');nodes.demoPin={value:'2468'};run('unlockDemo();publishOffering("burger");setTab("till")');
 run('acceptBasketPrices();checkout()');
 assert.equal(run('orders.length'),0);
 assert.equal(run('total()'),12.5);
});
test('simulated order retains locked price and vendor after later catalogue changes',()=>{
 const {run,nodes}=boot();
 run('add("burger");checkout()');
 assert.equal(run('orders[0].lines[0].p.price'),12.5);
 run('setTab("backoffice")');nodes.demoPin={value:'1357'};run('unlockDemo()');
 nodes.offerName={value:'Pattersons Burger'};nodes.offerPrice={value:'14.00'};nodes.offerAvailable={checked:true};
 run('stageOffering("burger");setTab("backoffice")');nodes.demoPin={value:'2468'};run('unlockDemo();publishOffering("burger")');
 assert.equal(run('orders[0].lines[0].p.price'),12.5);
 assert.equal(run('orders[0].lines[0].p.vendor'),'Pattersons');
});

test('shared ingredient demand blocks second item before overselling',()=>{
 const {run}=boot();
 run('demoSetStock("corona",5);add("corona");add("bucket")');
 assert.equal(run('cart.corona'),1);
 assert.equal(run('cart.bucket'),undefined);
 assert.equal(run('stock.corona'),5);
});
test('checkout refuses combined oversell after stock reduction without partial deductions',()=>{
 const {run,nodes}=boot();
 run('add("bucket");add("corona");demoSetStock("corona",5);checkout()');
 assert.equal(run('orders.length'),0);
 assert.equal(run('stock.corona'),5);
 assert.match(nodes.app.innerHTML,/Checkout blocked/);
});
test('successful mixed basket consumes shared ingredient exactly once',()=>{
 const {run}=boot();
 run('add("bucket");add("corona");checkout()');
 assert.equal(run('orders.length'),1);
 assert.equal(run('stock.corona'),18);
});

test('virtual room combines stock counted in separate physical areas',()=>{
 const {run,nodes}=boot();run('setTab("stock")');
 assert.match(nodes.app.innerHTML,/Virtual stockrooms/);
 assert.equal(run('stockroomStore.totals().vodka'),32);
 assert.equal(run('stockroomStore.countSheet("communal-spirits")[1].total'),32);
});
test('simulated mixed checkout depletes physical counts but preserves one virtual pool',()=>{
 const {run}=boot();run('add("pornstar");checkout()');
 assert.equal(run('orders.length'),1);
 assert.equal(run('stock.vodka'),31);
 assert.equal(run('stockroomStore.totals().vodka'),31);
 assert.equal(run('stockroomStore.snapshot().items.find(x=>x.id==="vodka").counts["main-bar"]'),15);
});
test('physical count adjustment changes availability on staff and QR',()=>{
 const {run,nodes}=boot();
 run('setTab("stock");adjustCount("cake","kitchen",-4)');
 assert.equal(run('stock.cake'),0);
 run('setTab("qr")');
 assert.match(nodes.app.innerHTML,/Cherry On Top Cake/);
 assert.equal(run('canAdd(products.find(p=>p.id==="cake"))'),false);
});
