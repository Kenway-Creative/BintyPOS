/* BintyPOS v0.2.8 — synchronous, in-memory inventory reservation simulator.
 * NOT a multi-device lock or durable transaction. consumeStock MUST be all-or-none.
 * For production, reserve/commit/expire and idempotency require one authoritative DB.
 */
(function(root,factory){
 const api=factory();
 if(typeof module==='object'&&module.exports)module.exports=api;
 root.BintyReservations=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
 'use strict';
 const copy=x=>JSON.parse(JSON.stringify(x));
 const positive=x=>Number.isSafeInteger(x)&&x>0;
 const validId=x=>typeof x==='string'&&/^[a-z0-9][a-z0-9-]*$/.test(x);
 const validKey=x=>typeof x==='string'&&/^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$/.test(x);
 function createStore({readStock,consumeStock,now=()=>Date.now(),defaultTtlMs=120000}={}){
  if(typeof readStock!=='function'||typeof consumeStock!=='function'||typeof now!=='function')throw Error('INVALID_RESERVATION_ADAPTER');
  if(!Number.isSafeInteger(defaultTtlMs)||defaultTtlMs<1000||defaultTtlMs>900000)throw Error('INVALID_RESERVATION_TTL');
  const records=new Map();
  function clock(){const t=now();if(!Number.isSafeInteger(t)||t<0)throw Error('INVALID_RESERVATION_CLOCK');return t}
  function demandsOf(input){
   if(!input||typeof input!=='object'||Array.isArray(input))throw Error('INVALID_RESERVATION_DEMAND');
   const pairs=Object.entries(input).sort(([a],[b])=>a.localeCompare(b));
   for(const [id,qty] of pairs)if(!validId(id)||!positive(qty))throw Error('INVALID_RESERVATION_DEMAND');
   return Object.fromEntries(pairs);
  }
  function stockNow(){
   const s=readStock();
   if(!s||typeof s!=='object'||Array.isArray(s))throw Error('INVALID_RESERVATION_STOCK');
   for(const [id,qty] of Object.entries(s))if(!validId(id)||!Number.isSafeInteger(qty)||qty<0)throw Error('INVALID_RESERVATION_STOCK');
   return {...s};
  }
  function sweep(t=clock()){
   for(const r of records.values())if(r.status==='held'&&t>=r.expiresAt)r.status='expired';
  }
  function availability(exceptKey){
   const available=stockNow();
   for(const r of records.values())if(r.status==='held'&&r.key!==exceptKey){
    for(const [id,qty] of Object.entries(r.demands))available[id]=Math.max(0,(available[id]??0)-qty);
   }
   return available;
  }
  function shortages(demands,exceptKey){
   const a=availability(exceptKey);
   return Object.entries(demands).filter(([id,qty])=>qty>(a[id]??0)).map(([id,qty])=>({ingredientId:id,required:qty,available:a[id]??0}));
  }
  function error(code,items){const e=Error(code);if(items)e.shortages=items;return e}
  function reserve({key,demands,ttlMs=defaultTtlMs}={}){
   if(!validKey(key))throw error('INVALID_IDEMPOTENCY_KEY');
   const requested=demandsOf(demands);
   if(!Number.isSafeInteger(ttlMs)||ttlMs<1000||ttlMs>900000)throw error('INVALID_RESERVATION_TTL');
   const t=clock();sweep(t);
   const existing=records.get(key);
   if(existing){if(JSON.stringify(existing.demands)!==JSON.stringify(requested))throw error('IDEMPOTENCY_CONFLICT');return copy(existing)}
   const missing=shortages(requested);
   if(missing.length)throw error('INSUFFICIENT_RESERVABLE_STOCK',missing);
   if(!Number.isSafeInteger(t+ttlMs))throw error('INVALID_RESERVATION_CLOCK');
   const r={key,demands:requested,status:'held',createdAt:t,expiresAt:t+ttlMs};
   records.set(key,r);return copy(r);
  }
  function commit(key){
   if(!validKey(key))throw error('INVALID_IDEMPOTENCY_KEY');
   sweep();const r=records.get(key);
   if(!r)throw error('UNKNOWN_RESERVATION');
   if(r.status==='committed')return copy(r);
   if(r.status!=='held')throw error('RESERVATION_NOT_ACTIVE');
   const missing=shortages(r.demands,key);
   if(missing.length){r.status='conflicted';throw error('RESERVATION_STOCK_CONFLICT',missing)}
   // The adapter must apply ALL movements atomically or throw with no side effects.
   const committedAt=clock();
   const outcome=consumeStock(copy(r.demands));
   r.status='committed';r.movements=copy(outcome?.movements||[]);r.committedAt=committedAt;
   return copy(r);
  }
  function release(key){
   if(!validKey(key))throw error('INVALID_IDEMPOTENCY_KEY');
   sweep();const r=records.get(key);
   if(!r)throw error('UNKNOWN_RESERVATION');
   if(r.status==='committed')throw error('RESERVATION_ALREADY_COMMITTED');
   if(r.status==='held')r.status='released';
   return copy(r);
  }
  function status(key){sweep();const r=records.get(key);return r?copy(r):null}
  function available(){sweep();return availability()}
  function activeCount(){sweep();return [...records.values()].filter(r=>r.status==='held').length}
  return Object.freeze({reserve,commit,release,status,available,activeCount});
 }
 return Object.freeze({createStore});
});
