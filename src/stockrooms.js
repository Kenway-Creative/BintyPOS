/* BintyPOS v0.2.7: virtual stockrooms are logical categories, not physical locations.
 * Pure demo state; server must enforce identity, concurrency and durable stock movements.
 */
(function(root,factory){
 const api=factory();
 if(typeof module==='object'&&module.exports)module.exports=api;
 root.BintyStockrooms=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
 'use strict';
 const goodId=x=>typeof x==='string'&&/^[a-z0-9][a-z0-9-]*$/.test(x);
 const count=x=>Number.isSafeInteger(x)&&x>=0;
 const copy=x=>JSON.parse(JSON.stringify(x));
 function createStore(input){
  if(!input||!Array.isArray(input.rooms)||!Array.isArray(input.locations)||!Array.isArray(input.items))throw Error('INVALID_STOCKROOM_MODEL');
  const rooms=copy(input.rooms),locations=copy(input.locations),items=copy(input.items);
  function unique(rows){
   const seen=new Set();
   for(const row of rows){if(!row||!goodId(row.id)||typeof row.name!=='string'||!row.name.trim()||seen.has(row.id))throw Error('INVALID_STOCKROOM_ID');seen.add(row.id)}
   return seen;
  }
  const roomIds=unique(rooms),locationIds=unique(locations);
  if(!roomIds.size||!locationIds.size)throw Error('EMPTY_STOCKROOM_MODEL');
  const itemIds=new Set();
  for(const item of items){
   if(!item||!goodId(item.id)||itemIds.has(item.id)||!roomIds.has(item.roomId)||!item.counts||typeof item.counts!=='object'||Array.isArray(item.counts))throw Error('INVALID_STOCKROOM_ITEM');
   itemIds.add(item.id);
   for(const [locationId,quantity] of Object.entries(item.counts))if(!locationIds.has(locationId)||!count(quantity))throw Error('INVALID_LOCATION_COUNT');
  }
  function itemFor(id){const item=items.find(x=>x.id===id);if(!item)throw Error('UNKNOWN_INGREDIENT');return item}
  function total(item){
   let n=0;
   for(const quantity of Object.values(item.counts)){n+=quantity;if(!Number.isSafeInteger(n))throw Error('STOCKROOM_OVERFLOW')}
   return n;
  }
  function totals(){const result={};for(const item of items)result[item.id]=total(item);return result}
  function snapshot(){return {rooms:copy(rooms),locations:copy(locations),items:copy(items)}}
  function countSheet(roomId){
   if(!roomIds.has(roomId))throw Error('UNKNOWN_STOCKROOM');
   return items.filter(x=>x.roomId===roomId).sort((a,b)=>a.id.localeCompare(b.id)).map(item=>({
    ingredientId:item.id,roomId,total:total(item),
    locations:locations.map(loc=>({id:loc.id,name:loc.name,quantity:item.counts[loc.id]||0}))
   }));
  }
  function setCount(ingredientId,locationId,quantity){
   if(!locationIds.has(locationId)||!count(quantity))throw Error('INVALID_LOCATION_COUNT');
   const item=itemFor(ingredientId);
   const next={...item.counts,[locationId]:quantity};
   let n=0;for(const q of Object.values(next)){n+=q;if(!Number.isSafeInteger(n))throw Error('STOCKROOM_OVERFLOW')}
   item.counts=next;
   return total(item);
  }
  function moveRoom(ingredientId,roomId){
   if(!roomIds.has(roomId))throw Error('UNKNOWN_STOCKROOM');
   const item=itemFor(ingredientId);item.roomId=roomId;return countSheet(roomId);
  }
  function consume(demands){
   if(!demands||typeof demands!=='object'||Array.isArray(demands))throw Error('INVALID_STOCKROOM_DEMAND');
   const shortages=[];
   for(const [id,quantity] of Object.entries(demands)){
    if(!goodId(id)||!Number.isSafeInteger(quantity)||quantity<=0)throw Error('INVALID_STOCKROOM_DEMAND');
    const item=itemFor(id),available=total(item);
    if(quantity>available)shortages.push({ingredientId:id,required:quantity,available});
   }
   if(shortages.length){const error=Error('INSUFFICIENT_SHARED_STOCK');error.shortages=shortages.sort((a,b)=>a.ingredientId.localeCompare(b.ingredientId));throw error}
   const movements=[];
   for(const id of Object.keys(demands).sort()){
    const item=itemFor(id);let remaining=demands[id];
    for(const locationId of Object.keys(item.counts).sort()){
     const used=Math.min(remaining,item.counts[locationId]);if(!used)continue;
     item.counts[locationId]-=used;remaining-=used;
     movements.push({ingredientId:id,roomId:item.roomId,locationId,quantity:used});
     if(!remaining)break;
    }
   }
   return {totals:totals(),movements};
  }
  return Object.freeze({snapshot,totals,countSheet,setCount,moveRoom,consume,rooms:()=>copy(rooms),locations:()=>copy(locations)});
 }
 return Object.freeze({createStore});
});