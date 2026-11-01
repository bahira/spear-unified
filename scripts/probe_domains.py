"""Small cross-domain feasibility probes; analytic targets, not empirical laws."""
import json
import math
from pathlib import Path
import sys
import time
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from spear.discovery import discover
from spear.core import compile_tree
root=Path(__file__).resolve().parents[1]
cases=[('signal','sin(x)',-0.1,0.1,2e-4,math.sin),
       ('normalized_thermal_decay','exp(-x)',0,0.1,0.01,lambda x:math.exp(-x)),
       ('ml_activation','tanh(x)',-0.1,0.1,0.001,math.tanh)]
start=time.perf_counter();results=[]
for domain,formula,lo,hi,tolerance,oracle in cases:
    r=discover({'formula':formula,'lo':lo,'hi':hi,'max_abs_error':tolerance,'generations':30,'population':64})
    if r['status']=='ok':
        fn=compile_tree(r['tree']);xs=[lo+(hi-lo)*i/1000 for i in range(1001)]
        error=max(abs(fn(x)-oracle(x)) for x in xs)
        r['independent_probe']={'reference':'Python math analytical target','points':1001,'endpoints_included':True,'max_abs_error':error,'within_requested_tolerance':error<=tolerance}
    results.append({'use_case':domain,'result':r})
report={'elapsed_seconds':time.perf_counter()-start,'note':'Synthetic analytical targets with illustrative tolerances. No real-world domain validation, causal inference, novel law or speedup demonstrated. Candidates not promoted.','results':results}
(root/'reports/domain-probes.json').write_text(json.dumps(report,indent=2)+'\n')
for x in results:
 r=x['result'];print(x['use_case'],r['status'],r.get('formula'),r.get('independent_probe'))
print('Total seconds:',report['elapsed_seconds'])
