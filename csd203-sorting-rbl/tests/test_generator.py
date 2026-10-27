import hashlib
import random
import struct
import unittest
from data.generate import generate, input_sha256, output_check, MAX_VALUE

class GeneratorTests(unittest.TestCase):
    def test_sorted_derived_and_multiset(self):
        d1=generate("D1",2000,2026)
        self.assertEqual(generate("D2",2000,2026),sorted(d1))
        self.assertEqual(generate("D4",2000,2026),sorted(d1,reverse=True))
        self.assertEqual(sorted(generate("D3",2000,2026)),sorted(d1))
        rng=random.Random(12026);expected=sorted(d1)
        for _ in range(2):
            i,j=rng.sample(range(2000),2);expected[i],expected[j]=expected[j],expected[i]
        self.assertEqual(generate("D3",2000,2026),expected)
    def test_d5_and_d6(self):
        self.assertLessEqual(len(set(generate("D5",200,10,k=2))),2)
        original=generate("D1",17,203)
        data=generate("D6",17,203,runs=4)
        self.assertEqual(sorted(data),sorted(original))
        start=0
        for size in [5,4,4,4]:
            self.assertEqual(data[start:start+size],sorted(original[start:start+size]));start+=size
    def test_deterministic_empty_small_and_domain(self):
        for i in range(1,7):
            kwargs={"k":10} if i==5 else {"runs":16} if i==6 else {}
            for n in [0,1,2,100]:
                a=generate(f"D{i}",n,203,**kwargs)
                self.assertEqual(a,generate(f"D{i}",n,203,**kwargs))
                self.assertEqual(len(a),n)
                self.assertTrue(all(0<=x<=MAX_VALUE for x in a))
    def test_checksum_known_encoding(self):
        self.assertEqual(input_sha256([0,MAX_VALUE]),hashlib.sha256(struct.pack("<II",0,MAX_VALUE)).hexdigest())
        self.assertEqual(output_check([1,2,3]),"1026")
    def test_invalid(self):
        for args,kw in [(("D0",1,203),{}),(("D1",-1,203),{}),(("D5",1,203),{}),(("D6",1,203),{}),(("D1",1,203),{"k":2})]:
            with self.assertRaises(ValueError):generate(*args,**kw)
