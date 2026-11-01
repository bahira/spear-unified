import test from 'node:test';
import assert from 'node:assert/strict';
import {grid,errorMax,benchmark} from '../benchmark_discovery.mjs';

test('positive domain includes both bounds',()=>{
  const xs=grid(0.1,2,17);assert.equal(xs[0],0.1);assert.equal(xs.at(-1),2);assert.ok(xs.every(x=>x>0));
});
test('reject nonfinite values and errors',()=>{
  for(const v of [NaN,Infinity,-Infinity])assert.throws(()=>errorMax([v],[1]));
  assert.throws(()=>errorMax([1e308],[-1e308]));
  assert.throws(()=>grid(2,1));
});
test('identity benchmark uses supplied domain and strong baseline',()=>{
  const r=benchmark({config:{formula:'exp(log(x))',lo:0.1,hi:2},tree:{o:'var',n:'x'},formula:'x',requested_max_abs_error:1e-12},'x');
  assert.deepEqual(r.domain,[0.1,2]);assert.equal(r.eligible,true);assert.equal(r.strong_baseline.max_abs_error,0);
  assert.equal(r.comparison.pairs.length,21);
});
