/* BintyPOS inventory preflight v0.2.6. Pure, synchronous, browser/Node demo only.
 * Server must repeat this check inside an atomic reservation transaction.
 * Quantities are integer demo stock units, not production measurement units.
 */
(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  root.BintyInventory=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';
  const count=n=>Number.isSafeInteger(n)&&n>=0;
  const positive=n=>Number.isSafeInteger(n)&&n>0;
  function preflight(lines,products,stock){
    if(!Array.isArray(lines)||!Array.isArray(products)||!stock||typeof stock!=='object'||Array.isArray(stock))throw Error('INVALID_INVENTORY_INPUT');
    for(const [id,amount] of Object.entries(stock))if(!id||!count(amount))throw Error('INVALID_STOCK');
    const byId=new Map();
    for(const product of products){
      if(!product||typeof product.id!=='string'||!product.id||byId.has(product.id))throw Error('INVALID_CATALOGUE');
      byId.set(product.id,product);
    }
    const demands=Object.create(null);
    for(const line of lines){
      const id=line?.productId;
      if(typeof id!=='string'||!positive(line.quantity))throw Error('INVALID_ORDER_LINE');
      const product=byId.get(id);
      if(!product||product.available===false)throw Error('PRODUCT_UNAVAILABLE');
      const recipe=product.recipe;
      if(!recipe||typeof recipe!=='object'||Array.isArray(recipe))throw Error('INVALID_RECIPE');
      for(const [ingredient,units] of Object.entries(recipe)){
        if(!ingredient||!positive(units))throw Error('INVALID_RECIPE');
        const needed=units*line.quantity;
        const total=(demands[ingredient]||0)+needed;
        if(!Number.isSafeInteger(total))throw Error('INVENTORY_OVERFLOW');
        demands[ingredient]=total;
      }
    }
    const shortages=Object.keys(demands).sort().filter(id=>demands[id]>(stock[id]??0)).map(id=>({ingredientId:id,required:demands[id],available:stock[id]??0}));
    return {ok:shortages.length===0,demands:{...demands},shortages};
  }
  function consume(lines,products,stock){
    const result=preflight(lines,products,stock);
    if(!result.ok){const error=Error('INSUFFICIENT_SHARED_STOCK');error.shortages=result.shortages;throw error}
    const next={...stock};
    for(const [id,amount] of Object.entries(result.demands))next[id]=(next[id]??0)-amount;
    return {stock:next,demands:result.demands};
  }
  return Object.freeze({preflight,consume});
});
