import math
import unittest
from spear.core import Registry, Router, compile_tree, pdiv

class Checks(unittest.TestCase):
    def test_silu_reference(self):
        r = Registry()
        for i in range(-80,81):
            x = i/10
            self.assertAlmostEqual(r.compute('silu',x), x/(1+math.exp(-x)), places=12)

    def test_gelu_reference(self):
        r = Registry()
        for i in range(-80,81):
            x=i/10
            self.assertLess(abs(r.compute('gelu',x)-0.5*x*(1+math.erf(x/math.sqrt(2)))), 3e-5)

    def test_numeric_rails(self):
        self.assertEqual(pdiv(1,0), 1e4)
        self.assertEqual(pdiv(1,-1e-9), -1e4)
        self.assertEqual(pdiv(1e9,1), 1e4)
        exp=compile_tree({'o':'exp','c':[{'o':'var','n':'x'}]})
        self.assertEqual(exp(1000),math.exp(50))
        for x in (float('nan'),float('inf')):
            with self.assertRaises(ValueError): Registry().compute('silu',x)

    def test_no_silent_fallback(self):
        r=Router()
        for kind in ('browser','llm'):
            self.assertEqual(r.run({'kind':kind})['status'],'unavailable')
        self.assertEqual(r.run({'kind':'compute','kernel':'unknown','x':1})['status'],'unsupported')
        with self.assertRaises(ValueError): compile_tree({'o':'execute'})

if __name__=='__main__': unittest.main()
