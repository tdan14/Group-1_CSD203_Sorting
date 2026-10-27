"""Các test TODO hiện SKIP rõ tên. Bật flag khi module thực sự sẵn sàng."""
import random
import unittest
from data.generate import generate
from src.contracts import METRIC_FIELDS
from src.registry import ALGORITHMS, STABLE, is_ready, resolve
EDGES = [[],[7],[2,1],[3,3,3],[0,2147483647,0]]

class Record:
    def __init__(self,key,order):self.key,self.order=key,order
    def __lt__(self,other):return self.key<other.key

def correctness(name):
    def test(self):
        if not is_ready(name):self.skipTest(name+" chưa triển khai")
        fn=resolve(name)
        for original in EDGES:
            with self.subTest(original=original):
                a=original.copy();result=fn(a)
                output=result if name=="lib-sorted" else a
                if name!="lib-sorted":self.assertIsNone(result)
                self.assertEqual(output,sorted(original))
        rng=random.Random(203)
        for index in range(1000):
            family=index%6+1;n=rng.randrange(201);seed=rng.randrange(2**31)
            kw={"k":rng.choice([2,10,1000])} if family==5 else {"runs":rng.choice([2,16,256])} if family==6 else {}
            original=generate(f"D{family}",n,seed,**kw);a=original.copy();result=fn(a)
            with self.subTest(case=index,dataset=family):self.assertEqual(result if name=="lib-sorted" else a,sorted(original))
    return test

def counted(name):
    def test(self):
        if not (is_ready(name) and is_ready(name,"count")):self.skipTest(name+" count chưa triển khai")
        plain,measure=resolve(name),resolve(name,"count")
        rng=random.Random(203)
        for original in EDGES+[[rng.randrange(10) for _ in range(200)],list(range(65,-1,-1))]:
            a,b=original.copy(),original.copy();plain(a);metrics=measure(b)
            self.assertEqual(a,b);self.assertEqual(b,sorted(original));self.assertEqual(set(metrics),set(METRIC_FIELDS))
            for field in (("array_reads","array_writes") if name=="radix" else ("key_comparisons",)):
                self.assertIs(type(metrics[field]),int);self.assertGreaterEqual(metrics[field],0)
    return test

def stability(name):
    def test(self):
        if not is_ready(name):self.skipTest(name+" stability chưa triển khai")
        original=[Record((i*37)%13,i) for i in range(1000)]
        expected=sorted(original,key=lambda r:r.key)
        a=original.copy();resolve(name)(a)
        self.assertEqual([r.order for r in a],[r.order for r in expected])
    return test

class AlgorithmTests(unittest.TestCase):pass
for _name in ALGORITHMS:
    _safe=_name.replace("-","_")
    setattr(AlgorithmTests,"test_correct_"+_safe,correctness(_name))
    if _name!="lib-sorted":setattr(AlgorithmTests,"test_count_"+_safe,counted(_name))
    if _name in STABLE:setattr(AlgorithmTests,"test_stable_"+_safe,stability(_name))
