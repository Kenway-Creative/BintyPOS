/* BintyPOS outlet offering workflow v0.2.4.
 * Pure in-memory demo, NOT authentication, persistence or an API.
 * Server must derive actor scope from verified identity, never browser input.
 */
(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  root.BintyOfferings=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';
  const copy=value=>JSON.parse(JSON.stringify(value));
  const fields=['name','price','available'];
  function actorRole(actor){
    if(!actor||typeof actor!=='object'||typeof actor.id!=='string'||!actor.id.trim())throw Error('INVALID_ACTOR');
    if(actor.role==='venue_admin')return 'venue_admin';
    if(actor.role==='outlet_manager'&&typeof actor.outlet==='string'&&actor.outlet.trim())return 'outlet_manager';
    throw Error('INVALID_ACTOR');
  }
  function checkScope(actor,product,adminOnly=false){
    const role=actorRole(actor);
    if(adminOnly&&role!=='venue_admin')throw Error('VENUE_APPROVAL_REQUIRED');
    if(role==='outlet_manager'&&actor.outlet!==product.vendor)throw Error('OUTLET_SCOPE_DENIED');
    return role;
  }
  function normalisePatch(input,product){
    if(!input||typeof input!=='object'||Array.isArray(input))throw Error('INVALID_OFFERING_PATCH');
    const keys=Object.keys(input);
    if(!keys.length||keys.some(k=>!fields.includes(k)))throw Error('INVALID_OFFERING_PATCH');
    const patch={};
    for(const k of keys){
      const v=input[k];
      if(k==='name'){
        if(typeof v!=='string'||!v.trim()||v.trim().length>80)throw Error('INVALID_NAME');
        patch.name=v.trim();
      }else if(k==='price'){
        if(typeof v!=='number'||!Number.isFinite(v)||v<0||v>100000||Math.round(v*100)!==v*100&&Math.abs(Math.round(v*100)-v*100)>1e-7)throw Error('INVALID_PRICE');
        patch.price=v;
      }else if(k==='available'){
        if(typeof v!=='boolean')throw Error('INVALID_AVAILABILITY');
        patch.available=v;
      }
    }
    if(keys.every(k=>patch[k]===product[k]))throw Error('NO_CHANGES');
    return patch;
  }
  function createStore(initialProducts){
    if(!Array.isArray(initialProducts)||!initialProducts.length)throw Error('INVALID_PRODUCTS');
    const live=new Map(),drafts=new Map(),events=[];
    for(const product of initialProducts){
      if(!product||typeof product.id!=='string'||!product.id||typeof product.vendor!=='string'||!product.vendor||live.has(product.id))throw Error('INVALID_PRODUCT_ID');
      live.set(product.id,{...copy(product),available:product.available!==false,version:1});
    }
    function requireProduct(id){const p=live.get(id);if(!p)throw Error('UNKNOWN_PRODUCT');return p}
    function record(action,id,actor,details={}){
      events.push(copy({sequence:events.length+1,action,productId:id,actorId:actor.id,role:actor.role,outlet:actor.outlet||null,...details}));
    }
    return Object.freeze({
      published:()=>copy([...live.values()]),
      product:id=>copy(requireProduct(id)),
      draft:id=>{requireProduct(id);return drafts.has(id)?copy(drafts.get(id)):null},
      pending:()=>copy([...drafts.values()]),
      audit:()=>copy(events),
      stage:(id,input,actor)=>{
        const p=requireProduct(id);checkScope(actor,p);
        if(drafts.has(id))throw Error('DRAFT_ALREADY_EXISTS');
        const changes=normalisePatch(input,p);
        const draft={productId:id,outlet:p.vendor,baseVersion:p.version,changes,requestedBy:actor.id,status:'pending'};
        drafts.set(id,draft);
        record('offering.draft_staged',id,actor,{baseVersion:p.version,changes});
        return copy(draft);
      },
      discard:(id,actor)=>{
        const p=requireProduct(id);checkScope(actor,p);
        const d=drafts.get(id);if(!d)throw Error('NO_PENDING_DRAFT');
        if(actor.role!=='venue_admin'&&d.requestedBy!==actor.id)throw Error('DRAFT_OWNER_REQUIRED');
        drafts.delete(id);record('offering.draft_discarded',id,actor);
      },
      reject:(id,actor,reason='Not approved')=>{
        const p=requireProduct(id);checkScope(actor,p,true);
        if(!drafts.has(id))throw Error('NO_PENDING_DRAFT');
        if(typeof reason!=='string'||!reason.trim()||reason.length>200)throw Error('INVALID_REASON');
        drafts.delete(id);record('offering.draft_rejected',id,actor,{reason:reason.trim()});
      },
      publish:(id,actor,expectedVersion)=>{
        const p=requireProduct(id);checkScope(actor,p,true);
        if(!Number.isInteger(expectedVersion)||expectedVersion!==p.version)throw Error('OFFERING_VERSION_CONFLICT');
        const d=drafts.get(id);if(!d)throw Error('NO_PENDING_DRAFT');
        if(d.baseVersion!==p.version)throw Error('OFFERING_VERSION_CONFLICT');
        const next={...p,...copy(d.changes),version:p.version+1};
        live.set(id,next);drafts.delete(id);
        record('offering.published',id,actor,{fromVersion:p.version,toVersion:next.version,changes:d.changes});
        return copy(next);
      }
    });
  }
  return Object.freeze({createStore,normalisePatch});
});
