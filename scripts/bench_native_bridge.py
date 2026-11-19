"""Bounded Python/C buffer experiment; no installation or runtime promotion."""
from array import array
import ctypes
import hashlib
import json
import math
from pathlib import Path
import platform
import shutil
import statistics
import subprocess
import sys
import tempfile
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.native_probe import CODE

BUDGET=3e-6
# Reuse the original ref/approx definitions rather than copying the polynomial.
PREFIX=CODE.split('static double now(void)',1)[0]
SOURCE=PREFIX+r'''
size_t bridge_sin(const double *xs, double *out, size_t n, int approximate) {
    size_t count=0;
    for(size_t i=0;i<n;i++) {
        if(approximate && fabs(xs[i])<=1.0) {out[i]=approx(xs[i]);count++;}
        else out[i]=ref(xs[i]);
    }
    return count;
}
'''
FLAGS=['-O2','-std=c11','-fPIC','-shared','-fno-fast-math','-ffp-contract=off','-fno-builtin-sin']

def build_bridge(directory):
    cc=shutil.which('cc')
    if not cc or platform.system()!='Linux':raise RuntimeError('Experiment requires Linux with an existing C compiler')
    src=Path(directory)/'bridge.c';target=Path(directory)/'bridge.so';src.write_text(SOURCE)
    subprocess.run([cc,*FLAGS,str(src),'-lm','-o',str(target)],check=True,capture_output=True,text=True,timeout=5)
    lib=ctypes.CDLL(str(target));fn=lib.bridge_sin
    fn.argtypes=[ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double),ctypes.c_size_t,ctypes.c_int]
    fn.restype=ctypes.c_size_t
    return fn

def validate(xs):
    if not isinstance(xs,array) or xs.typecode!='d' or xs.itemsize!=ctypes.sizeof(ctypes.c_double):
        raise ValueError("Expected native array('d')")
    if len(xs)>65536 or not all(math.isfinite(x) for x in xs):
        raise ValueError('Expected at most 65536 finite inputs')

def python_reference(xs):
    validate(xs)
    return array('d',map(math.sin,xs)),0

def native(xs,fn,tolerance=0):
    validate(xs)
    if type(tolerance) not in (int,float):raise ValueError('Invalid tolerance')
    try:valid=math.isfinite(tolerance) and tolerance>=0
    except OverflowError:valid=False
    if not valid:raise ValueError('Invalid tolerance')
    out=array('d',[0.0])*len(xs)
    view=ctypes.c_double*len(xs)
    used=fn(view.from_buffer(xs),view.from_buffer(out),len(xs),int(tolerance>=BUDGET))
    return out,used

def main():
    started=time.perf_counter();results=[];sink=0.0
    with tempfile.TemporaryDirectory(prefix='spear-native-bridge-') as directory:
        build_start=time.perf_counter();fn=build_bridge(directory);build_ms=(time.perf_counter()-build_start)*1000
        for n,passes in [(1,100),(64,16),(4096,2),(65536,1)]:
            xs=array('d',(-1+2*i/max(1,n-1) for i in range(n)))
            variants={'python':lambda:python_reference(xs),'c_reference':lambda:native(xs,fn,0),'c_approx':lambda:native(xs,fn,BUDGET)}
            checked={name:f() for name,f in variants.items()}
            error=max(abs(y-math.sin(x)) for x,y in zip(xs,checked['c_approx'][0]))
            if not math.isfinite(error) or error>BUDGET:raise ValueError('Precision budget exceeded')
            for _ in range(3):
                for f in variants.values():f()
            names=list(variants);raw={name:[] for name in names}
            for rep in range(11):
                order=names[rep%3:]+names[:rep%3]
                if rep%2:order.reverse()
                for name in order:
                    t=time.perf_counter_ns()
                    for _ in range(passes):
                        out,_count=variants[name]();sink+=out[-1]
                    raw[name].append((time.perf_counter_ns()-t)/passes)
            med={name:statistics.median(values) for name,values in raw.items()}
            results.append({'size':n,'passes':passes,'max_abs_error':error,'approximated':checked['c_approx'][1],
                'median_call_ns':med,'speedup_approx_vs_python':med['python']/med['c_approx'],
                'speedup_approx_vs_c_reference':med['c_reference']/med['c_approx'],'raw_call_ns':raw})
    report={'date':'2026-11-05','status':'ok','python':platform.python_version(),'platform':platform.platform(),
        'compiler':shutil.which('cc'),'flags':FLAGS,'source_sha256':hashlib.sha256(SOURCE.encode()).hexdigest(),
        'source':'ref/approx prefix reused from scripts/native_probe.py; classical Taylor7, not GP discovery',
        'domain':[-1,1],'requested_max_abs_error':BUDGET,'warmup':3,'repetitions':11,'build_ms':build_ms,
        'elapsed_seconds':time.perf_counter()-started,'results':results,'sink':sink,
        'included':'Finite input scan, output allocation, ctypes buffer views, C call, tolerance validation and output use. Python baseline has same array input/output and finite scan. Rotated/reversed order.',
        'excluded':'Construction of input array, compilation and cold load excluded from call timings (build reported separately); CLI/JSON startup, input list conversion and application pipeline excluded.',
        'limitations':'Short noisy VM experiment on synthetic inputs. No runtime integration, backend auto-selection, continuous error certification or client gains. Requires an existing native array(d); conversion costs can remove the benefit.'}
    (ROOT/'reports/native-bridge-20261105.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='results'},indent=2))
    for r in results:print(r['size'],r['median_call_ns'],r['speedup_approx_vs_python'],r['max_abs_error'])

if __name__=='__main__':main()
