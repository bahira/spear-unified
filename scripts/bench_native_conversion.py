"""List/JSON costs around the optional buffer experiment; no runtime selection."""
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
from scripts.bench_native_bridge import BUDGET,FLAGS,SOURCE,build_bridge,native


def validate_list(values):
    if not isinstance(values,list) or len(values)>65536:
        raise ValueError('Expected at most 65536 finite numeric list entries')
    try:valid=all(type(x) in (int,float) and math.isfinite(x) for x in values)
    except OverflowError:valid=False
    if not valid:raise ValueError('Expected finite numeric entries')


def list_reference(values):
    validate_list(values)
    return list(map(math.sin,values)),0


def list_native(values,fn,tolerance=0):
    validate_list(values)
    out,used=native(array('d',values),fn,tolerance)
    return list(out),used


def json_call(payload,operation):
    out,used=operation(json.loads(payload))
    return json.dumps(out,allow_nan=False),used


def main():
    started=time.perf_counter();results=[];sink=0
    with tempfile.TemporaryDirectory(prefix='spear-conversions-') as directory:
        t=time.perf_counter();fn=build_bridge(directory);build_ms=(time.perf_counter()-t)*1000
        for mode in ('list','json'):
            for n,passes in [(1,30),(64,4),(4096,1),(65536,1)]:
                xs=[-1+2*i/max(1,n-1) for i in range(n)]
                operations={'python':list_reference,'c_reference':lambda x:list_native(x,fn,0),'c_approx':lambda x:list_native(x,fn,BUDGET)}
                if mode=='json':
                    payload=json.dumps(xs,allow_nan=False)
                    variants={k:(lambda op=op:json_call(payload,op)) for k,op in operations.items()}
                else:variants={k:(lambda op=op:op(xs)) for k,op in operations.items()}
                checked={k:op() for k,op in variants.items()}
                out=checked['c_approx'][0]
                if mode=='json':out=json.loads(out)
                error=max(abs(y-math.sin(x)) for x,y in zip(xs,out))
                if not math.isfinite(error) or error>BUDGET:raise ValueError('Precision budget exceeded')
                for _ in range(2):
                    for op in variants.values():op()
                names=list(variants);raw={k:[] for k in names}
                for rep in range(7):
                    order=names[rep%3:]+names[:rep%3]
                    if rep%2:order.reverse()
                    for k in order:
                        t=time.perf_counter_ns()
                        for _ in range(passes):
                            out,_used=variants[k]();sink+=len(out)
                        raw[k].append((time.perf_counter_ns()-t)/passes)
                med={k:statistics.median(v) for k,v in raw.items()}
                results.append({'mode':mode,'size':n,'passes':passes,'max_abs_error':error,
                  'approximated':checked['c_approx'][1],'median_call_ns':med,
                  'speedup_approx_vs_python':med['python']/med['c_approx'],
                  'speedup_approx_vs_c_reference':med['c_reference']/med['c_approx'],
                  'serialized_output_bytes':{k:len(v[0].encode()) for k,v in checked.items()} if mode=='json' else None,
                  'raw_call_ns':raw})
    report={'date':'2026-11-08','status':'ok','python':platform.python_version(),'platform':platform.platform(),
      'compiler_flags':FLAGS,'source_sha256':hashlib.sha256(SOURCE.encode()).hexdigest(),
      'domain':[-1,1],'requested_max_abs_error':BUDGET,'warmup':2,'repetitions':7,'build_ms':build_ms,
      'elapsed_seconds':time.perf_counter()-started,'results':results,'sink':sink,
      'included':'List: numeric validation, list-to-array, native finite scan, output allocation, ctypes call, array-to-list. JSON: the same plus input json.loads and output json.dumps for every variant. Rotated/reversed order.',
      'excluded':'Compilation/cold library load (build separately reported), synthetic input generation and initial input JSON encoding, process/CLI startup, network and actual application. Runtime remains unchanged.',
      'limitations':'Classical Taylor7, not GP discovery. Synthetic inputs and short noisy VM measurements; approximated numbers may serialize to different strings/lengths. No automatic backend or client savings established.'}
    (ROOT/'reports/native-conversion-20261108.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    print('build_ms',build_ms,'elapsed_seconds',report['elapsed_seconds'])
    for r in results:print(r['mode'],r['size'],r['median_call_ns'],r['speedup_approx_vs_python'],r['max_abs_error'])

if __name__=='__main__':main()
