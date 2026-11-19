"""Synthetic domain-mix probe; reuse the existing buffer bridge unchanged."""
from array import array
import hashlib
import json
import math
from pathlib import Path
import platform
import statistics
import sys
import tempfile
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.bench_native_bridge import BUDGET,FLAGS,SOURCE,build_bridge,native,python_reference


def mixed_values(n,outside_fraction):
    """Interleave a known count of out-of-domain points, no client distribution."""
    count=round(n*outside_fraction)
    xs=array('d')
    for i in range(n):
        outside=(i+1)*count//n != i*count//n
        x=2+6*i/max(1,n-1) if outside else -1+2*i/max(1,n-1)
        if outside and i%2:x=-x
        xs.append(x)
    return xs


def main():
    started=time.perf_counter();results=[];sink=0.0
    with tempfile.TemporaryDirectory(prefix='spear-mixed-domain-') as directory:
        t=time.perf_counter();fn=build_bridge(directory);build_ms=(time.perf_counter()-t)*1000
        for n in (4096,65536):
            for fraction in (0,0.5,1):
                xs=mixed_values(n,fraction);outside=sum(abs(x)>1 for x in xs)
                operations={'python':lambda:python_reference(xs),'c_reference':lambda:native(xs,fn,0),'c_mixed':lambda:native(xs,fn,BUDGET)}
                checked={name:op() for name,op in operations.items()}
                out,used=checked['c_mixed']
                error=max(abs(y-math.sin(x)) for x,y in zip(xs,out))
                fallback_error=max((abs(y-math.sin(x)) for x,y in zip(xs,out) if abs(x)>1),default=0)
                if not math.isfinite(error) or error>BUDGET or used!=n-outside or fallback_error>1e-14:
                    raise ValueError('Domain/precision contract failed')
                for _ in range(2):
                    for op in operations.values():op()
                names=list(operations);raw={name:[] for name in names}
                for rep in range(7):
                    order=names[rep%3:]+names[:rep%3]
                    if rep%2:order.reverse()
                    for name in order:
                        t=time.perf_counter_ns();out,_=operations[name]();sink+=out[-1]
                        raw[name].append(time.perf_counter_ns()-t)
                med={name:statistics.median(values) for name,values in raw.items()}
                results.append({'size':n,'requested_outside_fraction':fraction,'outside_count':outside,'approximated':used,
                    'max_abs_error':error,'fallback_max_abs_error':fallback_error,'median_call_ns':med,
                    'speedup_mixed_vs_python':med['python']/med['c_mixed'],
                    'speedup_mixed_vs_c_reference':med['c_reference']/med['c_mixed'],'raw_call_ns':raw})
    report={'date':'2026-11-11','status':'ok','python':platform.python_version(),'platform':platform.platform(),
      'flags':FLAGS,'source_sha256':hashlib.sha256(SOURCE.encode()).hexdigest(),'approximation_domain':[-1,1],
      'outside_absolute_range':[2,8],'requested_max_abs_error':BUDGET,'warmup':2,'repetitions':7,
      'build_ms':build_ms,'elapsed_seconds':time.perf_counter()-started,'results':results,'sink':sink,
      'included':'Existing native array input; finite scan, output allocation, ctypes views/call, tolerance check and output consumption. Python reference uses same input and output types. Rotated/reversed timing order.',
      'excluded':'Input construction, compilation/cold loading (build reported separately), list/JSON conversion, process startup, network and application pipeline.',
      'limitations':'Deterministically interleaved synthetic mixtures, not client traffic or random workload sampling. Fixed fractions may not reflect branch/cache behavior of a real system. Classical Taylor7, not GP discovery; no runtime change, selection policy or client gain.'}
    (ROOT/'reports/native-mixed-20261111.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    print('build_ms',build_ms,'elapsed_seconds',report['elapsed_seconds'])
    for r in results:print(r['size'],r['requested_outside_fraction'],r['approximated'],r['median_call_ns'],r['speedup_mixed_vs_c_reference'],r['max_abs_error'])

if __name__=='__main__':main()
