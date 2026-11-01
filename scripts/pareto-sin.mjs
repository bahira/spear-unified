// Known Taylor approximations, not discovered candidates. Local scalar JS loops.
import fs from 'node:fs';
const N=4097,passes=16,repeats=31,warmup=40;
const kernels={
  sin:x=>Math.sin(x),
  linear:x=>x,
  taylor3:x=>x*(1-x*x/6),
  taylor5:x=>x*(1+x*x*(-1/6+x*x/120)),
};
const median=a=>[...a].sort((a,b)=>a-b)[Math.floor(a.length/2)];
const quantile=(a,q)=>[...a].sort((a,b)=>a-b)[Math.floor((a.length-1)*q)];
let sink=0;
const report={node:process.version,platform:process.platform,arch:process.arch,
  methodology:{points:N,passes,repeats,warmup,allocation:'Fresh Float64Array for every function call, same loop and callback structure',order:'Rotated and reversed across repetitions',timing:'Median ns/element; p10/p90 and min/max report dispersion',note:'Known approximations, not outputs of the discovery engine. No C/SIMD or general speedup claim.'},domains:[]};
for(const bound of [0.1,1]){
 const xs=Float64Array.from({length:N},(_,i)=>-bound+2*bound*i/(N-1));
 const outputs=Object.fromEntries(Object.entries(kernels).map(([k,fn])=>[k,()=>{const out=new Float64Array(N);for(let i=0;i<N;i++)out[i]=fn(xs[i]);return out;}]));
 const stats={};
 for(const [name,fn] of Object.entries(kernels)){
  let max=0,sum=0;
  for(const x of xs){const err=fn(x)-Math.sin(x);max=Math.max(max,Math.abs(err));sum+=err*err;}
  stats[name]={max_abs_error:max,mse:sum/N,endpoint_errors:[-bound,bound].map(x=>Math.abs(fn(x)-Math.sin(x)))};
 }
 for(let i=0;i<warmup;i++)for(const fn of Object.values(outputs))sink+=fn()[i%N];
 const times=Object.fromEntries(Object.keys(kernels).map(k=>[k,[]]));
 const names=Object.keys(kernels);
 for(let rep=0;rep<repeats;rep++){
  const rotated=[...names.slice(rep%names.length),...names.slice(0,rep%names.length)];
  if(rep%2)rotated.reverse();
  for(const name of rotated){const start=performance.now();for(let j=0;j<passes;j++)sink+=outputs[name]()[j];times[name].push((performance.now()-start)*1e6/(passes*N));}
 }
 const baseline=median(times.sin);
 for(const name of names){const t=times[name];Object.assign(stats[name],{median_ns_per_element:median(t),p10_ns:quantile(t,0.1),p90_ns:quantile(t,0.9),min_ns:Math.min(...t),max_ns:Math.max(...t),speedup_vs_sin:baseline/median(t)});}
 // Measured speed/error frontier only, no statistical significance claim.
 for(const name of names)stats[name].dominated_on_this_run=names.some(other=>other!==name&&stats[other].max_abs_error<=stats[name].max_abs_error&&stats[other].median_ns_per_element<=stats[name].median_ns_per_element&&(stats[other].max_abs_error<stats[name].max_abs_error||stats[other].median_ns_per_element<stats[name].median_ns_per_element));
 report.domains.push({domain:[-bound,bound],results:stats});
}
report.sink=sink;
fs.writeFileSync('reports/pareto-sin.json',JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report,null,2));
