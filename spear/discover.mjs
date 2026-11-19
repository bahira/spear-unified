import {evolve,setSeed,parseFormula,collectVarNames,evaluateNode,serializeNode,nodeToString,estimateCost} from '../vendor/superspear/engine.ts';
const q=JSON.parse(process.argv[2]);
const target=parseFormula(q.formula);
if(collectVarNames(target).some(x=>x!=='x')) throw new Error('Only variable x supported');
setSeed(q.seed);
const xs=Float64Array.from({length:q.rows},(_,i)=>q.lo+(q.hi-q.lo)*(i+0.5)/q.rows);
const ys=evaluateNode(target,{x:xs},xs.length);
if(!ys.every(Number.isFinite)) throw new Error('Non-finite target');
const score=(node)=>{
 const p=evaluateNode(node,{x:xs},xs.length);
 let mse=0,max=0;
 for(let i=0;i<p.length;i++) {if(!Number.isFinite(p[i]))return {fitness:-1e100,size:node.size};const e=p[i]-ys[i];mse+=e*e;max=Math.max(max,Math.abs(e));}
 return {fitness:-(mse/p.length+0.05*max),size:node.size};
};
const start=performance.now();
const r=evolve({variables:['x'],constRange:[-3,3],ops:['add','sub','mul','sq','neg'],maxDepth:4,populationSize:q.population,generations:q.generations},score);
// Preserve the 127 interior holdout points and add both exact domain bounds.
// Validation remains outside fitness and cannot change the selected candidate.
const interior=Float64Array.from({length:127},(_,i)=>q.lo+(q.hi-q.lo)*(i+0.271828)/127);
const base=Float64Array.of(q.lo,...interior,q.hi);
// Fixed extra validation only; neither base nor midpoints are used by fitness.
const midpoints=Float64Array.from({length:base.length-1},(_,i)=>(base[i]+base[i+1])/2);
const hx=Float64Array.of(...base,...midpoints);
const truth=evaluateNode(target,{x:hx},hx.length),pred=evaluateNode(r.best,{x:hx},hx.length);
let mse=0,max=0;
for(let i=0;i<hx.length;i++){const e=pred[i]-truth[i];if(!Number.isFinite(e))throw new Error('Non-finite holdout');mse+=e*e;max=Math.max(max,Math.abs(e));}
if(!Number.isFinite(mse)||!Number.isFinite(max))throw new Error('Non-finite holdout metrics');
console.log(JSON.stringify({status:'ok',kind:'candidate',formula:nodeToString(r.best),tree:serializeNode(r.best),holdout:{mse:mse/hx.length,max_abs_error:max,rows:hx.length,endpoints_included:true,midpoints_included:true,base_rows:base.length,midpoint_rows:midpoints.length},cost_units:estimateCost(r.best),duration_ms:performance.now()-start,evaluations:r.evals,config:q,note:'Candidate only; holdout uses upstream numerical semantics; cost is modelled, no measured speedup.'}));
