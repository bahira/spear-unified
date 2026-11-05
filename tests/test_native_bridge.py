from array import array
import math
import platform
import shutil
import tempfile
import unittest
from scripts.bench_native_bridge import BUDGET,build_bridge,native,python_reference

@unittest.skipUnless(shutil.which('cc') and platform.system()=='Linux','Optional experiment needs Linux/C compiler')
class NativeBridgeChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory=tempfile.TemporaryDirectory(prefix='spear-bridge-test-')
        cls.addClassCleanup(cls.directory.cleanup)
        cls.fn=staticmethod(build_bridge(cls.directory.name))

    def test_accuracy_and_domain_fallback(self):
        xs=array('d',[-2,math.nextafter(-1,-2)]+[-1+2*i/4096 for i in range(4097)]+[math.nextafter(1,2),2])
        original=xs[:];out,used=native(xs,self.fn,BUDGET)
        self.assertEqual(xs,original)
        self.assertEqual(used,4097)
        self.assertLessEqual(max(abs(y-math.sin(x)) for x,y in zip(xs,out)),BUDGET)
        for i in [0,1,-2,-1]:self.assertAlmostEqual(out[i],math.sin(xs[i]),places=14)

    def test_strict_tolerance_and_empty(self):
        xs=array('d',[-1,-.1,0,.1,1,2])
        for tol in [0,1e-9,math.nextafter(BUDGET,0)]:
            out,used=native(xs,self.fn,tol)
            self.assertEqual(used,0)
            for x,y in zip(xs,out):self.assertAlmostEqual(y,math.sin(x),places=14)
        self.assertEqual(native(array('d'),self.fn,BUDGET),(array('d'),0))

    def test_invalid_input_and_tolerance(self):
        for xs in [[],array('f',[0]),array('d',[float('nan')]),array('d',[float('inf')]),array('d',[0])*65537]:
            with self.assertRaises(ValueError):native(xs,self.fn,BUDGET)
            with self.assertRaises(ValueError):python_reference(xs)
        for tol in [-1,True,'1',float('nan'),float('inf'),10**400]:
            with self.assertRaises(ValueError):native(array('d'),self.fn,tol)
