import contextlib
import io
import unittest
from unittest.mock import patch
from bench.plan import official_plan
from bench.runner import run_single_trial
from bench.summarize import summarize
from bench.worker import run_trial

class HarnessTests(unittest.TestCase):
    def case(self,mode="time"):
        return dict(algo="lib-sorted",dataset="D1",n=100,seed=2026,mode=mode,rq="smoke")
    def test_time_and_memory_in_separate_workers(self):
        timed=run_single_trial(self.case("time"),"integration-test","development")
        memory=run_single_trial(self.case("mem"),"integration-test","development")
        self.assertEqual(timed["status"],"ok");self.assertEqual(memory["status"],"ok")
        self.assertNotEqual(timed["elapsed_ms"],"");self.assertEqual(timed["mem_peak_bytes"],"")
        self.assertNotEqual(memory["mem_peak_bytes"],"");self.assertEqual(memory["elapsed_ms"],"")
        self.assertEqual(timed["output_check"],memory["output_check"])
    def test_timeout_not_completed_time(self):
        result=run_single_trial(self.case(),"integration-test","development",timeout=.000001)
        self.assertEqual(result["status"],"timeout");self.assertEqual(result["elapsed_ms"],"")
    def test_wrong_and_exception_status(self):
        for fn,status in [(lambda a:a,"wrong"),(lambda a:(_ for _ in ()).throw(MemoryError()),"oom"),(lambda a:(_ for _ in ()).throw(RecursionError()),"crash")]:
            with patch("bench.worker.get_algorithm_callable",return_value=fn),contextlib.redirect_stderr(io.StringIO()):
                result=run_trial("integration-test","smoke","quick","D1",100,2026,"time",
                                 code_commit="integration-test",machine_id="development")
            self.assertEqual(result["status"],status)
            self.assertFalse(result["oracle_match"])
    def test_plan_dedup(self):
        plan=official_plan();keys=[]
        for c in plan:
            keys.append(tuple((k,str(v)) for k,v in sorted(c.items()) if k!="rq"))
            self.assertFalse(c["algo"]=="lib-sorted" and c["mode"]=="count")
        self.assertEqual(len(keys),len(set(keys)))
        self.assertTrue(any(c["rq"]=="RQ1+RQ2+RQ3" for c in plan))
    def test_summary_failure_and_seed_completeness(self):
        rows=[dict(seed=str(seed),status="ok",elapsed_ms=str(value),official="True",mode="time") for seed,value in zip([2026,2027,2028],[1,4,2])]
        result=summarize(rows)[0]
        self.assertEqual(result["elapsed_ms_median"],2);self.assertTrue(result["complete"])
        rows[2]["status"]="timeout"
        result=summarize(rows)[0]
        self.assertFalse(result["complete"]);self.assertEqual(result["failed_count"],1)
        with self.assertRaises(ValueError):summarize([rows[0],rows[0]])
