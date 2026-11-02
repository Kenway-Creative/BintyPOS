/* BintyPOS immutable basket v0.2.5.
 * Browser/Node demonstration only. Checkout validation MUST be repeated atomically
 * on a trusted server with stock reservation and idempotent payment handling.
 */
(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  root.BintyBasket=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';
  const copy=value=>JSON.parse(JSON.stringify(value));
  function toMinor(pounds){
    if(typeof pounds!=='number'||!Number.isFinite(pounds)||pounds<0)throw Error('INVALID_PRICE');
    const minor=Math.round(pounds*100);
    if(!Number.isSafeInteger(minor)||Math.abs(pounds*100-minor)>1e-7)throw Error('INVALID_PRICE');
    return minor;
  }
  function checkedProduct(product){
    if(!product||typeof product.id!=='string'||!product.id.trim()||
       typeof product.vendor!=='string'||!product.vendor.trim()||
       typeof product.name!=='string'||!product.name.trim()||
       !Number.isSafeInteger(product.version)||product.version<1)throw Error('INVALID_PRODUCT');
    return {
      productId:product.id,
      productVersion:product.version,
      vendor:product.vendor,
      name:product.name,
      unitPriceMinor:toMinor(product.price)
    };
  }
  function createStore(){
    const lines=new Map();
    function snapshot(){
      const result=[...lines.values()].map(copy);
      const subtotalMinor=result.reduce((sum,line)=>{
        const next=sum+line.unitPriceMinor*line.quantity;
        if(!Number.isSafeInteger(next))throw Error('BASKET_TOTAL_OVERFLOW');
        return next;
      },0);
      return {currency:'GBP',lines:result,subtotalMinor};
    }
    function review(products){
      if(!Array.isArray(products))throw Error('INVALID_CATALOGUE');
      const byId=new Map(products.map(p=>[p.id,p]));
      const conflicts=[];
      for(const line of lines.values()){
        const current=byId.get(line.productId);
        if(!current){conflicts.push({productId:line.productId,code:'PRODUCT_REMOVED'});continue}
        if(current.available===false){conflicts.push({productId:line.productId,code:'PRODUCT_UNAVAILABLE'});continue}
        const latest=checkedProduct(current);
        if(latest.productVersion!==line.productVersion||
           latest.unitPriceMinor!==line.unitPriceMinor||
           latest.vendor!==line.vendor){
          conflicts.push({
            productId:line.productId,code:'CATALOGUE_CHANGED',
            fromVersion:line.productVersion,toVersion:latest.productVersion,
            fromPriceMinor:line.unitPriceMinor,toPriceMinor:latest.unitPriceMinor
          });
        }
      }
      return {...snapshot(),conflicts};
    }
    return Object.freeze({
      add(product){
        if(product&&product.available===false)throw Error('PRODUCT_UNAVAILABLE');
        const current=checkedProduct(product);
        const old=lines.get(current.productId);
        if(old){
          if(old.quantity>=999)throw Error('QUANTITY_LIMIT');
          old.quantity++;
        }else lines.set(current.productId,{...current,quantity:1});
        return snapshot();
      },
      remove(productId){
        const old=lines.get(productId);
        if(!old)return snapshot();
        if(old.quantity===1)lines.delete(productId);
        else old.quantity--;
        return snapshot();
      },
      quantity:productId=>lines.get(productId)?.quantity||0,
      snapshot,
      review,
      acceptPublished(products){
        const current=review(products);
        if(current.conflicts.some(x=>x.code!=='CATALOGUE_CHANGED'))throw Error('BASKET_UNAVAILABLE');
        const byId=new Map(products.map(p=>[p.id,p]));
        for(const [id,line] of lines){
          const latest=checkedProduct(byId.get(id));
          lines.set(id,{...latest,quantity:line.quantity});
        }
        return snapshot();
      },
      validatedOrder(products){
        const current=review(products);
        if(current.conflicts.length)throw Error('BASKET_REVIEW_REQUIRED');
        if(!current.lines.length)throw Error('EMPTY_BASKET');
        return current;
      },
      clear(){lines.clear();return snapshot()}
    });
  }
  return Object.freeze({createStore,toMinor});
});
