import json
import math
import platform
import shutil
import tempfile
import unittest
from unittest.mock import Mock
from scripts.bench_native_conversion import BUDGET,build_bridge,json_call,list_native,list_reference

class ConversionValidation(unittest.TestCase):
    def test_invalid_list_never_reaches_native_function(self):
        fn=Mock(side_effect=AssertionError('Invalid input reached C'))
        for values in (None,{},[True],['0'],[float('nan')],[float('inf')],[10**400],[0]*65537):
            with self.assertRaises(ValueError):list_native(values,fn,BUDGET)
            with self.assertRaises(ValueError):list_reference(values)
        fn.assert_not_called()

@unittest.skipUnless(shutil.which('cc') and platform.system()=='Linux','Optional Linux/C experiment')
class NativeConversionChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory(prefix='spear-conversion-test-')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.fn=staticmethod(build_bridge(cls.temp.name))

    def test_list_and_json_accuracy_and_fallback(self):
        values=[-2,-1,0,0.5,1,2];original=values[:]
        out,count=list_native(values,self.fn,BUDGET)
        self.assertEqual(values,original)
        self.assertIsInstance(out,list)
        self.assertEqual(count,4)
        self.assertLessEqual(max(abs(y-math.sin(x)) for x,y in zip(values,out)),BUDGET)
        payload,count=json_call(json.dumps(values),lambda x:list_native(x,self.fn,BUDGET))
        self.assertEqual(json.loads(payload),out)
        self.assertEqual(count,4)
        for i in (0,-1):self.assertAlmostEqual(out[i],math.sin(values[i]),places=14)

    def test_strict_reference_empty_and_invalid_json(self):
        values=[-1,-0.1,0,0.1,1,2]
        out,count=list_native(values,self.fn,1e-9)
        self.assertEqual(count,0)
        reference,_=list_reference(values)
        for a,b in zip(out,reference):self.assertAlmostEqual(a,b,places=14)
        self.assertEqual(list_native([],self.fn,BUDGET),([],0))
        self.assertEqual(json_call('[]',lambda x:list_native(x,self.fn,BUDGET)),('[]',0))
        for payload in ('[NaN]','[Infinity]','{"x":1}','[true]','not json'):
            with self.assertRaises(ValueError):json_call(payload,lambda x:list_native(x,self.fn,BUDGET))
