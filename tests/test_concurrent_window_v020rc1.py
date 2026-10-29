import sys,threading,time,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from hashburst_tep.poh.concurrent_window import ConcurrentEvaluationWindow
from hashburst_tep.poh import WindowError
from hashburst_tep.vdf.adapter import VDFAdapter,VDFResult

class ControlledAdapter(VDFAdapter):
 suite_id="controlled-test"
 def __init__(self):self.entered=threading.Event();self.release=threading.Event()
 def evaluate(self,challenge,iterations):
  self.entered.set()
  if not self.release.wait(2):raise RuntimeError("test release timeout")
  return VDFResult(bytes.fromhex("aa"*32),bytes.fromhex("bb"*32),iterations)
 def verify(self,challenge,result):return result.output==bytes.fromhex("aa"*32)

class ConcurrentWindowTests(unittest.TestCase):
 def test_registration_occurs_while_evaluate_is_active(self):
  a=ControlledAdapter();w=ConcurrentEvaluationWindow(a);w.start(bytes(32),1,64);w.wait_started(1);self.assertTrue(a.entered.wait(1))
  r=w.register(bytes.fromhex("11"*32));a.release.set();c=w.close(1)
  self.assertEqual(c.records,(r,));self.assertTrue(w.verify(c));self.assertGreater(w.timing.finished_monotonic_ns,w.timing.started_monotonic_ns)
 def test_registration_after_evaluation_is_rejected(self):
  a=ControlledAdapter();w=ConcurrentEvaluationWindow(a);w.start(bytes(32),1,64);w.wait_started(1);a.release.set();w.close(1)
  with self.assertRaises(WindowError):w.register(bytes.fromhex("22"*32))
 def test_failed_evaluation_is_abandoned_and_records_not_completed(self):
  class Failing(ControlledAdapter):
   def evaluate(self,challenge,iterations):self.entered.set();raise RuntimeError("injected failure")
  a=Failing();w=ConcurrentEvaluationWindow(a);w.start(bytes(32),1,64);w.wait_started(1)
  with self.assertRaises(RuntimeError):w.close(1)
  with self.assertRaises(WindowError):w.register(bytes.fromhex("33"*32))

if __name__=="__main__":unittest.main(verbosity=2)
