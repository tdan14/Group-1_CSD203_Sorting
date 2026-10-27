import contextlib
import io
import unittest
from unittest.mock import patch
from bench.plan import official_plan
from bench.runner import execute
from bench.summarize import summarize
from bench.worker import run

class HarnessTests(unittest.TestCase):
    def case(self,mode="time"):
        return dict(algorithm="lib-sorted",dataset="D1",n=100,seed=2026,mode=mode,rq="smoke")
    def test_time_and_memory_in_separate_workers(self):
        timed=execute(self.case("time"));memory=execute(self.case("mem"))
        self.assertEqual(timed["status"],"ok");self.assertEqual(memory["status"],"ok")
        self.assertIn("elapsed_ms",timed);self.assertNotIn("mem_peak_bytes",timed)
        self.assertIn("mem_peak_bytes",memory);self.assertNotIn("elapsed_ms",memory)
        self.assertEqual(timed["output_check"],memory["output_check"])
    def test_timeout_not_completed_time(self):
        result=execute(self.case(),timeout=.000001)
        self.assertEqual(result["status"],"timeout");self.assertNotIn("elapsed_ms",result)
    def test_wrong_and_exception_status(self):
        for fn,status in [(lambda a:a,"wrong"),(lambda a:(_ for _ in ()).throw(MemoryError()),"oom"),(lambda a:(_ for _ in ()).throw(RecursionError()),"crash")]:
            with patch("bench.worker.resolve",return_value=fn),contextlib.redirect_stderr(io.StringIO()):
                result=run(self.case())
            self.assertEqual(result["status"],status);self.assertNotIn("elapsed_ms",result)
    def test_plan_dedup(self):
        plan=official_plan();keys=[]
        for c in plan:
            keys.append(tuple((k,str(v)) for k,v in sorted(c.items()) if k!="rq"))
            self.assertFalse(c["algorithm"]=="lib-sorted" and c["mode"]=="count")
        self.assertEqual(len(keys),len(set(keys)))
        self.assertTrue(any(c["rq"]=="RQ1;RQ2;RQ3" for c in plan))
    def test_summary_failure_and_seed_completeness(self):
        rows=[dict(seed=str(seed),status="ok",elapsed_ms=str(value),official="True",mode="time") for seed,value in zip([2026,2027,2028],[1,4,2])]
        result=summarize(rows)[0]
        self.assertEqual(result["elapsed_ms_median"],2);self.assertTrue(result["complete"])
        rows[2]["status"]="timeout"
        result=summarize(rows)[0]
        self.assertFalse(result["complete"]);self.assertEqual(result["failed_count"],1)
        with self.assertRaises(ValueError):summarize([rows[0],rows[0]])
