import fs from 'node:fs';
import {pathToFileURL} from 'node:url';
import {parseFormula,parseNode,evaluateNode} from './vendor/superspear/engine.ts';

export function grid(lo,hi,n=4096){
  if(!Number.isFinite(lo)||!Number.isFinite(hi)||lo>=hi||!Number.isInteger(n)||n<2)throw new Error('Invalid benchmark domain/grid');
  return Float64Array.from({length:n},(_,i)=>lo+(hi-lo)*i/(n-1));
}
export function errorMax(a,b){
  if(a.length!==b.length||!a.length)throw new Error('Invalid output lengths');
  let error=0;
  for(let i=0;i<a.length;i++){
    const delta=Math.abs(a[i]-b[i]);
    if(!Number.isFinite(a[i])||!Number.isFinite(b[i])||!Number.isFinite(delta))throw new Error('Non-finite benchmark output');
    error=Math.max(error,delta);
  }
  return error;
}
const median=a=>[...a].sort((x,y)=>x-y)[Math.floor(a.length/2)];
let sink=0;
function compare(f,g,n){
  const repeats=21,inner=8;
  function time(fn){
    const t=performance.now();
    for(let i=0;i<inner;i++){const out=fn();sink+=out[i%out.length];}
    const ns=(performance.now()-t)*1e6/(n*inner);
    if(!Number.isFinite(ns)||ns<=0)throw new Error('Invalid timing');
    return ns;
  }
  for(let i=0;i<30;i++){f();g();}
  const pairs=[];
  for(let i=0;i<repeats;i++){
    let base,candidate;
    if(i%2){candidate=time(g);base=time(f);}else{base=time(f);candidate=time(g);}
    pairs.push({base_ns:base,candidate_ns:candidate});
  }
  return {base_ns_per_element:median(pairs.map(p=>p.base_ns)),candidate_ns_per_element:median(pairs.map(p=>p.candidate_ns)),
    median_paired_speedup:median(pairs.map(p=>p.base_ns/p.candidate_ns)),pairs};
}
export function benchmark(r,strongBaseline){
  const {lo,hi}=r.config,xs=grid(lo,hi);
  const base=parseFormula(r.config.formula),candidate=parseNode(r.tree);
  const f=()=>evaluateNode(base,{x:xs},xs.length),g=()=>evaluateNode(candidate,{x:xs},xs.length);
  const error=errorMax(f(),g());
  const result={target:r.config.formula,candidate:r.formula,domain:[lo,hi],max_abs_error:error,
    eligible:error<=r.requested_max_abs_error,comparison:compare(f,g,xs.length)};
  if(strongBaseline){
    const tree=parseFormula(strongBaseline),h=()=>{
      const values=evaluateNode(tree,{x:xs},xs.length);
      // A bare variable aliases input upstream; copy for equal owned-output semantics.
      return values===xs?new Float64Array(values):values;
    };
    result.strong_baseline={formula:strongBaseline,output_semantics:'Owned Float64Array; bare-variable output copied',max_abs_error:errorMax(h(),g()),comparison:compare(h,g,xs.length)};
  }
  return result;
}
if(process.argv[1]&&import.meta.url===pathToFileURL(process.argv[1]).href){
  const runs=JSON.parse(fs.readFileSync('reports/discovery.json','utf8'));
  const extra=JSON.parse(fs.readFileSync('reports/search-agent.json','utf8')).results.find(r=>r.config.formula==='exp(log(x))');
  const results=[...runs.map(r=>benchmark(r)),benchmark(extra,'x')];
  const report={node:process.version,platform:process.platform,arch:process.arch,points:4096,repeats:21,inner:8,warmup:30,
    method:'Per-candidate domain including endpoints; same upstream evaluator; allocations included; warmed alternating paired measurements. No native claim; timings exclude discovery.',results,sink};
  const json=JSON.stringify(report,(_k,v)=>{if(typeof v==='number'&&!Number.isFinite(v))throw new Error('Non-finite report');return v;},2);
  fs.writeFileSync('reports/discovery-speed.json',json+'\n');
  console.log(JSON.stringify(results.map(r=>({target:r.target,domain:r.domain,error:r.max_abs_error,eligible:r.eligible,speedup:r.comparison.median_paired_speedup,versus_strong:r.strong_baseline?.comparison.median_paired_speedup})),null,2));
}
