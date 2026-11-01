#!/usr/bin/env python3
"""Small standalone C/libm versus Taylor probe. No installs, no fast-math."""
import json
import math
from pathlib import Path
import platform
import shutil
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
CODE = r'''
#define _POSIX_C_SOURCE 200809L
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#define N 65537
#define INNER 16
#define REPS 9
#if defined(__GNUC__)
#define NOINLINE __attribute__((noinline))
#else
#define NOINLINE
#endif
static volatile double sink;
static NOINLINE double ref(double x) { return sin(x); }
static NOINLINE double approx(double x) {
    const double z=x*x;
    return x*(1.0+z*(-1.0/6.0+z*(1.0/120.0-z/5040.0)));
}
static double now(void) {
    struct timespec ts;
    if(clock_gettime(CLOCK_MONOTONIC,&ts)) exit(3);
    return (double)ts.tv_sec+(double)ts.tv_nsec*1e-9;
}
static NOINLINE double measure(double (*fn)(double), const double *xs) {
    double start=now();
    for(int r=0;r<INNER;r++) {
        double sum=0;
        for(int i=0;i<N;i++) sum+=fn(xs[i]);
        sink+=sum;
    }
    return (now()-start)*1e9/(N*INNER);
}
int main(void) {
    double *xs=malloc(sizeof(double)*N);
    if(!xs) return 2;
    double err=0,sq=0;
    for(int i=0;i<N;i++) {
        xs[i]=-1.0+2.0*(double)i/(N-1);
        double e=approx(xs[i])-ref(xs[i]);
        if(!isfinite(e)) return 4;
        err=fmax(err,fabs(e));sq+=e*e;
    }
    for(int i=0;i<3;i++){measure(ref,xs);measure(approx,xs);}
    double a[REPS],b[REPS];
    for(int r=0;r<REPS;r++) {
        if(r%2) {b[r]=measure(approx,xs);a[r]=measure(ref,xs);}
        else {a[r]=measure(ref,xs);b[r]=measure(approx,xs);}
    }
    printf("{\"reference_ns\":[");
    for(int r=0;r<REPS;r++)printf("%s%.9g",r?",":"",a[r]);
    printf("],\"candidate_ns\":[");
    for(int r=0;r<REPS;r++)printf("%s%.9g",r?",":"",b[r]);
    printf("],\"max_abs_error\":%.17g,\"mse\":%.17g,\"sink\":%.17g}\n",err,sq/N,sink);
    free(xs);return 0;
}
'''

def main():
    compiler=shutil.which('cc') or shutil.which('gcc') or shutil.which('clang')
    report={'status':'unavailable','compiler':compiler,'platform':platform.platform(),
            'domain':[-1,1],'points':65537,'inner':16,'repeats':9,
            'candidate':'x*(1+x*x*(-1/6+x*x*(1/120-x*x/5040)))',
            'candidate_origin':'Classical seventh-order Taylor polynomial, not discovered by Superspear',
            'reference':'C libm sin(double)',
            'method':'Same noinline function call and checksum reduction for both; warmup, alternating order, nine repetitions. Scalar double, no fast-math.',
            'limitations':'Includes function-call and reduction overhead; one process on this VM. No Python/JS integration overhead measured; no claim of general sin replacement or SIMD gain.'}
    if compiler:
        try:
            with tempfile.TemporaryDirectory(prefix='spear-native-') as directory:
                src=Path(directory)/'probe.c';exe=Path(directory)/'probe'
                src.write_text(CODE)
                start=time.perf_counter()
                flags=['-O2','-std=c11','-fno-fast-math','-ffp-contract=off','-fno-builtin-sin']
                subprocess.run([compiler,*flags,str(src),'-lm','-o',str(exe)],capture_output=True,text=True,check=True,timeout=5)
                report['build_seconds']=time.perf_counter()-start
                start=time.perf_counter()
                run=subprocess.run([str(exe)],capture_output=True,text=True,check=True,timeout=5)
                report['run_seconds']=time.perf_counter()-start
                values=json.loads(run.stdout)
                if not all(math.isfinite(v) for k,v in values.items() if not isinstance(v,list)):
                    raise ValueError('Non-finite scalar metric')
                for k in ('reference_ns','candidate_ns'):
                    if not all(math.isfinite(v) and v>0 for v in values[k]):raise ValueError('Invalid timing')
                import statistics
                a=statistics.median(values['reference_ns']);b=statistics.median(values['candidate_ns'])
                report.update(values)
                report.update(status='ok',compiler_flags=flags,reference_median_ns=a,candidate_median_ns=b,speedup=a/b,
                              requested_max_abs_error=1e-4,accepted_on_probe=values['max_abs_error']<=1e-4)
        except (subprocess.SubprocessError,ValueError) as error:
            report.update(status='error',reason=str(error))
    (ROOT/'reports/native-probe.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    (ROOT/'reports/native-probe.md').write_text('# Sonde native C\n\n'+
        ('Résultat : %.2f× dans ce microbenchmark, erreur maximale %.3g sur [-1,1].\n\n'%(report['speedup'],report['max_abs_error']) if report['status']=='ok' else 'Indisponible ou échec ; voir le JSON.\n\n')+
        'Polynôme de Taylor classique d’ordre 7, pas une découverte Superspear. Référence libm sin(double), grille de 65 537 points incluant les bornes. Deux fonctions noinline, même coût de réduction, somme consommée dans une variable volatile, ordre alterné, médiane de neuf répétitions après préchauffage. Compilation -O2 sans fast-math et contraction FMA désactivée.\n\n'+
        'La mesure ne comprend pas un passage Python/C ni le routage et ne justifie pas un remplacement général de sin. Elle ne valide que la grille et le domaine annoncés, sur cette VM. Aucun fichier du runtime modifié.\n')
    print(json.dumps(report,indent=2,allow_nan=False))

if __name__=='__main__':main()
