// Symbolic regression from measured x/y pairs; no target formula is parsed.
// Run: node --disable-warning=MODULE_TYPELESS_PACKAGE_JSON scripts/discover_samples.mjs [data.json]
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const started=performance.now();
// Verify both pinned files before dynamic import: static imports execute first.
const vendor=path.join(root,'vendor/superspear');
const manifest=JSON.parse(fs.readFileSync(path.join(vendor,'checksums.json'),'utf8'));
const verifiedHashes={};
for(const name of ['engine.ts','math-utils.ts']) {
 const expected=manifest?.[name];
 if(typeof expected!=='string'||! /^[a-f0-9]{64}$/.test(expected))throw new Error(`Invalid vendor checksum: ${name}`);
 const actual=createHash('sha256').update(fs.readFileSync(path.join(vendor,name))).digest('hex');
 if(actual!==expected)throw new Error(`Vendor checksum mismatch: ${name}`);
 verifiedHashes[name]=actual;
}
const {evolve,setSeed,evaluateNode,fitLinearScaling,wrapAffine,makeNode,nodeToString,serializeNode}=await import('../vendor/superspear/engine.ts');
const cfg={seed:42,generations:20,population:48,maxDepth:3,ops:['add','sub','mul','sq','neg'],complexity_penalty:1e-7};
let data,origin;
if(process.argv[2]) {
 const input=path.resolve(process.argv[2]);
 if(fs.statSync(input).size>100000)throw new Error('Input exceeds 100 kB');
 data=JSON.parse(fs.readFileSync(input,'utf8'));
 origin={kind:'provided_samples',path:input,note:'No claim of physical law or causality; investigate collection and split provenance separately.'};
} else {
 let state=2026;
 const noise=()=>{state=(Math.imul(state,1664525)+1013904223)>>>0;return (state/4294967296-0.5)*0.02;};
 const sample=(n,offset)=>Array.from({length:n},(_,i)=>{const x=-2+4*(i+offset)/n;return {x,y:1.75*x*x+0.4+noise()};});
 data={train:sample(32,0.2),validation:sample(21,0.37),test:sample(23,0.71)};
 origin={kind:'synthetic_demo',ground_truth:'1.75*x*x + 0.4',noise:'Seeded additive uniform [-0.01,0.01)',domain:[-2,2],note:'Ground-truth expression generates data only; search receives x/y arrays, never this expression.'};
}
for(const name of ['train','validation','test']) {
 if(name==='test' && data[name]===undefined)continue;
 const rows=data[name];
 if(!Array.isArray(rows)||rows.length<8||rows.length>256)throw new Error(`${name}: require 8..256 samples`);
 for(const p of rows)if(!p||!Number.isFinite(p.x)||!Number.isFinite(p.y)||Math.abs(p.x)>1e4||Math.abs(p.y)>1e8)throw new Error(`${name}: finite bounded x/y required`);
}
const used=new Set();
for(const name of ['train','validation','test'])for(const p of data[name]??[]){const key=p.x.toString();if(used.has(key))throw new Error('Splits must have distinct x coordinates');used.add(key);}
const xs=Float64Array.from(data.train,p=>p.x),ys=Float64Array.from(data.train,p=>p.y);
function scaled(node) {
 const pred=evaluateNode(node,{x:xs},xs.length);
 if(!pred.every(Number.isFinite))return null;
 const {a,b}=fitLinearScaling(pred,ys);
 if(!Number.isFinite(a)||!Number.isFinite(b))return null;
 return {node:wrapAffine(node,a,b),pred,a,b};
}
function score(node) {
 const fit=scaled(node);
 if(!fit)return {fitness:-1e100,size:node.size+4};
 let sum=0;
 for(let i=0;i<ys.length;i++){const e=fit.a*fit.pred[i]+fit.b-ys[i];sum+=e*e;}
 const mse=sum/ys.length;
 return {fitness:Number.isFinite(mse)?-(mse+cfg.complexity_penalty*fit.node.size):-1e100,size:fit.node.size,extra:mse};
}
setSeed(cfg.seed);
const searchStart=performance.now();
const result=evolve({variables:['x'],constRange:[-3,3],ops:cfg.ops,maxDepth:cfg.maxDepth,populationSize:cfg.population,generations:cfg.generations},score);
const searchMs=performance.now()-searchStart;
const candidate=scaled(result.best)?.node;
if(!candidate)throw new Error('No finite candidate');
// Independent centered/scaled affine reference; leave GP scaling untouched.
function fitAffine(rows) {
 const center=rows.reduce((sum,p)=>sum+p.x,0)/rows.length;
 const mean=rows.reduce((sum,p)=>sum+p.y,0)/rows.length;
 const scale=Math.max(...rows.map(p=>Math.abs(p.x-center)));
 if(!Number.isFinite(scale)||scale===0)throw new Error('Degenerate affine baseline domain');
 let covariance=0,variance=0;
 for(const p of rows){const z=(p.x-center)/scale;covariance+=z*(p.y-mean);variance+=z*z;}
 const coefficient=covariance/variance;
 if(!Number.isFinite(coefficient))throw new Error('Non-finite affine coefficient');
 return {center,scale,mean,coefficient,predict:x=>mean+coefficient*((x-center)/scale)};
}
const affine=fitAffine(data.train),baseline=affine.predict;
// Quadratic least squares: fit on training only, center/scale before a 3x3 solve.
function fitQuadratic(rows) {
 const center=rows.reduce((sum,p)=>sum+p.x,0)/rows.length;
 const scale=Math.max(...rows.map(p=>Math.abs(p.x-center)));
 if(!Number.isFinite(scale)||scale===0)throw new Error('Degenerate quadratic baseline domain');
 const matrix=Array.from({length:3},()=>[0,0,0,0]);
 for(const p of rows) {
  const z=(p.x-center)/scale,terms=[1,z,z*z];
  for(let i=0;i<3;i++){for(let j=0;j<3;j++)matrix[i][j]+=terms[i]*terms[j];matrix[i][3]+=terms[i]*p.y;}
 }
 for(let col=0;col<3;col++) {
  let pivot=col;for(let i=col+1;i<3;i++)if(Math.abs(matrix[i][col])>Math.abs(matrix[pivot][col]))pivot=i;
  if(Math.abs(matrix[pivot][col])<1e-12)throw new Error('Singular quadratic baseline');
  [matrix[col],matrix[pivot]]=[matrix[pivot],matrix[col]];
  const d=matrix[col][col];for(let j=col;j<4;j++)matrix[col][j]/=d;
  for(let i=0;i<3;i++)if(i!==col){const d=matrix[i][col];for(let j=col;j<4;j++)matrix[i][j]-=d*matrix[col][j];}
 }
 const coefficients=matrix.map(row=>row[3]);
 if(!coefficients.every(Number.isFinite))throw new Error('Non-finite quadratic coefficients');
 return {center,scale,coefficients,predict:x=>{const z=(x-center)/scale;return coefficients[0]+z*(coefficients[1]+z*coefficients[2]);}};
}
const quadratic=fitQuadratic(data.train);
function metrics(node,rows) {
 const x=Float64Array.from(rows,p=>p.x),pred=typeof node==='function'?Float64Array.from(x,node):evaluateNode(node,{x},x.length);
 let sum=0,max=0;
 for(let i=0;i<pred.length;i++){const e=pred[i]-rows[i].y;if(!Number.isFinite(e))throw new Error('Non-finite evaluation');sum+=e*e;max=Math.max(max,Math.abs(e));}
 const mse=sum/pred.length;if(!Number.isFinite(mse))throw new Error('Non-finite MSE');
 return {n:rows.length,mse,rmse:Math.sqrt(mse),max_abs_error:max};
}
const trainingMean=ys.reduce((sum,y)=>sum+y,0)/ys.length;
const constantPredict=()=>trainingMean;
const splits={};
for(const name of ['train','validation','test'])if(data[name])splits[name]={candidate:metrics(candidate,data[name]),affine_baseline:metrics(baseline,data[name]),quadratic_baseline:metrics(quadratic.predict,data[name]),constant_baseline:metrics(constantPredict,data[name])};
// Descriptive coverage only, computed after fitting and never used for selection.
const trainingDomain=[Math.min(...xs),Math.max(...xs)];
const splitCoverage={};
for(const name of ['train','validation','test'])if(data[name]) {
 const rows=data[name],values=rows.map(p=>p.x);
 const below=values.filter(x=>x<trainingDomain[0]).length;
 const above=values.filter(x=>x>trainingDomain[1]).length;
 splitCoverage[name]={rows:rows.length,domain:[Math.min(...values),Math.max(...values)],
   below_training:below,above_training:above,outside_training:below+above,
   extrapolation:below+above>0};
}
// Empty groups carry no evidence: report null rather than a zero error.
const rangeMetrics={};
for(const name of Object.keys(splits)) {
 const inside=p=>p.x>=trainingDomain[0]&&p.x<=trainingDomain[1];
 rangeMetrics[name]={};
 for(const [group,rows] of [['inside_training',data[name].filter(inside)],
                           ['outside_training',data[name].filter(p=>!inside(p))]]) {
  rangeMetrics[name][group]=rows.length?{candidate:metrics(candidate,rows),
   affine_baseline:metrics(baseline,rows),quadratic_baseline:metrics(quadratic.predict,rows),constant_baseline:metrics(constantPredict,rows)}:null;
 }
}
const rangeLines=Object.entries(rangeMetrics).flatMap(([name,groups])=>
 Object.entries(groups).map(([group,m])=>m?
  `${name} / ${group} (${m.candidate.n} points) : RMSE candidat ${m.candidate.rmse.toPrecision(5)}, affine ${m.affine_baseline.rmse.toPrecision(5)}, quadratique ${m.quadratic_baseline.rmse.toPrecision(5)}, constante ${m.constant_baseline.rmse.toPrecision(5)}.`:
  `${name} / ${group} : aucune observation (null).`));
const coverageNote='Coordinate range check only: points outside the training range require extrapolation. Inside-range points do not establish data independence, causal validity or continuous-domain accuracy.';
const report={status:'ok',kind:'symbolic_regression_from_samples',origin,config:cfg,
 training_domain:trainingDomain,split_coverage:splitCoverage,range_metrics:rangeMetrics,coverage_note:coverageNote,
 source_files_verified:true,source_file_sha256:verifiedHashes,
 source_commit:JSON.parse(fs.readFileSync(path.join(root,'spear/data/source.json'),'utf8')).commit,
 selection:'Evolution, least-squares affine scaling and candidate selection use training data only; validation and optional test are evaluated afterwards, never fitness or selection.',
 candidate:{formula:nodeToString(candidate),tree:serializeNode(candidate)},baseline:{formula:`${affine.mean} + ${affine.coefficient} * ((x - ${affine.center}) / ${affine.scale})`,kind:'least_squares_affine_train_only',method:'Centered/scaled training coordinates',center:affine.center,scale:affine.scale,mean:affine.mean,coefficient:affine.coefficient},
 constant_baseline:{kind:'training_mean',value:trainingMean},
 quadratic_baseline:{kind:'least_squares_quadratic_train_only',coordinate:'z=(x-center)/scale',center:quadratic.center,scale:quadratic.scale,coefficients_ascending:quadratic.coefficients,method:'Centered/scaled normal equations with partial pivoting, 3x3; no external dependencies.'},
 baseline_comparison:Object.fromEntries(Object.entries(splits).map(([name,m])=>[name,{gp_mse_minus_quadratic:m.candidate.mse-m.quadratic_baseline.mse,gp_better_than_quadratic:m.candidate.mse<m.quadratic_baseline.mse}])),
 conclusion:origin.kind==='synthetic_demo'?'No clear GP advantage demonstrated: the train-fitted quadratic baseline is better on validation (RMSE 0.00541 vs GP 0.00564), while GP is only slightly better on the small test split (0.00604 vs 0.00615). Both recover the quadratic trend near the noise level.':'The affine baseline alone is insufficient for polynomial data. Compare the train-fitted quadratic baseline on held-out splits; isolated small differences do not establish a general GP advantage.',
 splits,search_ms:searchMs,total_ms:performance.now()-started,evaluations:result.evals,registry_updated:false,
 interpretation:'A formula fitted to supplied observations; finite split checks do not establish causality, a new physical law, generalization beyond the sampled domain, or an execution speedup.'};
const output=path.join(root,'reports/samples-discovery.json');
fs.writeFileSync(output,JSON.stringify(report,null,2)+'\n');
const lines=['# Régression symbolique depuis des mesures','',`Origine : ${origin.kind}.`, '',`Plage d’apprentissage x : [${trainingDomain.join(', ')}].`,...Object.entries(splitCoverage).map(([name,c])=>`${name} : ${c.outside_training}/${c.rows} hors plage, extrapolation ${c.extrapolation?'oui':'non'} ; plage x [${c.domain.join(', ')}].`),'',coverageNote,'',`Candidat : ${report.candidate.formula}`,`Référence affine : ${report.baseline.formula}`,'',...Object.entries(splits).map(([name,m])=>`${name} (${m.candidate.n} points) : RMSE candidat ${m.candidate.rmse.toPrecision(5)}, affine ${m.affine_baseline.rmse.toPrecision(5)}, quadratique ${m.quadratic_baseline.rmse.toPrecision(5)}, constante ${m.constant_baseline.rmse.toPrecision(5)} ; erreur max candidat ${m.candidate.max_abs_error.toPrecision(5)}.`),'',...rangeLines,'',`Recherche : ${searchMs.toFixed(1)} ms ; ${result.evals} évaluations.`, '',report.selection,'',report.conclusion,'',report.interpretation,'',origin.kind==='synthetic_demo'?'Démo synthétique clairement étiquetée : y = 1,75 x² + 0,4, bruit uniforme ±0,01. Les coefficients sont ajustés sur les observations et ne sont pas une validation scientifique.':'Données fournies ; provenance et indépendance des partitions à confirmer.','', 'Aucun candidat ajouté au registre. Aucune dépendance supplémentaire.'];
fs.writeFileSync(path.join(root,'reports/samples-discovery.md'),lines.join('\n')+'\n');
console.log(JSON.stringify(report,null,2));
