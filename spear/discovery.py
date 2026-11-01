"""Bounded subprocess adapter for the pinned Superspear search engine."""
import json
import math
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parent.parent

def discover(task):
    formula=task.get('formula')
    if not isinstance(formula,str) or not 1<=len(formula)<=256:
        raise ValueError('formula must contain 1..256 characters')
    tolerance=task.get('max_abs_error',1e-4)
    if type(tolerance) not in (int,float) or not math.isfinite(tolerance) or tolerance<0:
        raise ValueError('max_abs_error must be finite and nonnegative')
    cfg={'formula':formula}
    for key,default,lo,hi in [('rows',64,8,256),('generations',8,1,30),('population',32,8,64),('seed',42,0,4294967295)]:
        v=task.get(key,default)
        if type(v) is not int or not lo<=v<=hi: raise ValueError(f'{key} must be an integer in [{lo}, {hi}]')
        cfg[key]=v
    for key,default in [('lo',-2),('hi',2)]:
        v=task.get(key,default)
        if type(v) not in (int,float) or not math.isfinite(v) or abs(v)>1e4:raise ValueError('Invalid domain')
        cfg[key]=v
    if cfg['lo']>=cfg['hi']:raise ValueError('lo must be below hi')
    try:
        p=subprocess.run(['node','--disable-warning=MODULE_TYPELESS_PACKAGE_JSON','--max-old-space-size=128',str(ROOT/'spear/discover.mjs'),json.dumps(cfg)],capture_output=True,text=True,timeout=5,cwd=ROOT)
    except subprocess.TimeoutExpired:
        return {'status':'timeout','reason':'Search stopped after 5 seconds; registry unchanged'}
    except FileNotFoundError:
        return {'status':'unavailable','reason':'Discovery requires Node 22.18+ or 24+'}
    if p.returncode:
        return {'status':'error','reason':p.stderr[-1500:]}
    result=json.loads(p.stdout)
    result['accepted_on_probe']=result['holdout']['max_abs_error']<=tolerance
    result['requested_max_abs_error']=tolerance
    result['registry_updated']=False
    result['source_commit']=json.loads((ROOT/'spear/data/source.json').read_text())['commit']
    return result
