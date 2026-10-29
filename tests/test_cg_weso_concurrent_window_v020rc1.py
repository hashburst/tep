import sys,time,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from hashburst_tep.poh.concurrent_window import ConcurrentEvaluationWindow
from hashburst_tep.poh import WindowPhase
from hashburst_tep.vdf import CGWesoV1

class RealCGWesoConcurrentWindowTests(unittest.TestCase):
 def test_registration_overlaps_real_cg_weso_evaluation(self):
  w=ConcurrentEvaluationWindow(CGWesoV1())
  challenge=bytes.fromhex("5a"*32);rid=bytes.fromhex("71"*32)
  w.start(challenge,1,1_000_000)
  w.wait_started(2)
  self.assertIs(w.phase,WindowPhase.RUNNING)
  registered_ns=time.monotonic_ns()
  record=w.register(rid)
  self.assertIs(w.phase,WindowPhase.RUNNING,"CG-WESO completed before overlap could be demonstrated")
  candidate=w.close(30)
  self.assertEqual(candidate.records,(record,))
  self.assertTrue(w.verify(candidate))
  self.assertEqual(candidate.result.iterations,1_000_000)
  self.assertEqual(len(candidate.result.output),100)
  self.assertEqual(len(candidate.result.proof),100)
  self.assertLessEqual(w.timing.started_monotonic_ns,registered_ns)
  self.assertLess(registered_ns,w.timing.finished_monotonic_ns)

if __name__=="__main__":unittest.main(verbosity=2)
