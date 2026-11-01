import fs from 'node:fs';
import {parseFormula,parseNode,evaluateNode} from './vendor/superspear/engine.ts';
const runs=JSON.parse(fs.readFileSync('reports/discovery.json','utf8'));
const n=4096,repeats=21,inner=8;
const xs=Float64Array.from({length:n},(_,i)=>-2+4*i/(n-1));
const median=a=>[...a].sort((x,y)=>x-y)[Math.floor(a.length/2)];
let sink=0;
function time(fn){const t=performance.now();for(let i=0;i<inner;i++){const out=fn();sink+=out[i];}return (performance.now()-t)*1e6/(n*inner);}
const results=[];
for(const r of runs){
 const base=parseFormula(r.config.formula),candidate=parseNode(r.tree);
 const f=()=>evaluateNode(base,{x:xs},n),g=()=>evaluateNode(candidate,{x:xs},n);
 const a=f(),b=g();let err=0;for(let i=0;i<n;i++)err=Math.max(err,Math.abs(a[i]-b[i]));
 for(let i=0;i<30;i++){f();g();}
 const at=[],bt=[];
 for(let i=0;i<repeats;i++){if(i%2){bt.push(time(g));at.push(time(f));}else{at.push(time(f));bt.push(time(g));}}
 results.push({target:r.config.formula,candidate:r.formula,max_abs_error:err,eligible:err<=r.requested_max_abs_error,base_ns_per_element:median(at),candidate_ns_per_element:median(bt),speedup:median(at)/median(bt),base_range_ns:[Math.min(...at),Math.max(...at)],candidate_range_ns:[Math.min(...bt),Math.max(...bt)]});
}
// Hand-written JS loop: practical baseline for the accepted x² candidate, same output allocation.
const square=r=>{const out=new Float64Array(n);for(let i=0;i<n;i++)out[i]=r(xs[i]);return out;};
const direct=()=>square(x=>x*x),discovered=()=>square(x=>x*x);
for(let i=0;i<30;i++){direct();discovered();}
const a=[],b=[];for(let i=0;i<repeats;i++){if(i%2){b.push(time(discovered));a.push(time(direct));}else{a.push(time(direct));b.push(time(discovered));}}
const report={node:process.version,platform:process.platform,arch:process.arch,points:n,repeats,inner,warmup:30,domain:[-2,2],method:'Same upstream vector evaluator and Float64Array allocations; warmed, alternating order, median. Timings exclude discovery. No C/SIMD claim.',results,direct_square_control:{note:'Target x*x and discovered sq(x) both lower to the same multiplication; identical hand-written implementation, noise control only.',base_ns_per_element:median(a),candidate_ns_per_element:median(b),speedup:median(a)/median(b)},sink};
fs.writeFileSync('reports/discovery-speed.json',JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));
