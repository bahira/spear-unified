"""Bounded local probe: no downloads, training, or external service calls."""
import json
import math
import platform
import statistics
import time
from pathlib import Path
from spear.core import Registry, compile_tree

r=Registry()
xs=[-8+16*i/1000 for i in range(1001)]
report={'python':platform.python_version(),'platform':platform.platform(),
        'source_commit':r.source['commit'],'probe_range':[-8,8],
        'note':'Scalar Python probe, not upstream C/WASM results. Fast variants measured but not enabled.',
        'kernels':{}}
for name in r.records:
    reference=(lambda x:x/(1+math.exp(-x))) if name=='silu' else (lambda x:0.5*x*(1+math.erf(x/math.sqrt(2))))
    variants={'reference':reference,'champion':r.functions[name]}
    if 'fastTree' in r.records[name]:variants['fast']=compile_tree(r.records[name]['fastTree'])
    results={}
    for variant,fn in variants.items():
        timings=[]
        for _ in range(5):
            start=time.perf_counter_ns()
            values=[fn(x) for x in xs]
            timings.append((time.perf_counter_ns()-start)/len(xs))
        errors=[abs(v-reference(x)) for x,v in zip(xs,values)]
        results[variant]={'median_ns_per_element':round(statistics.median(timings),1),
                          'max_abs_error':max(errors)}
    report['kernels'][name]=results
out=Path('reports/baseline.json');out.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
