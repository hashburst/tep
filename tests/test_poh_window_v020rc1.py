import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from hashburst_tep.poh.window import EvaluationWindow,WindowPhase,WindowError
from hashburst_tep.vdf import DeterministicTestVDF

class WindowTests(unittest.TestCase):
 def setUp(self):self.w=EvaluationWindow(DeterministicTestVDF());self.c=bytes.fromhex("ab"*32)
 def test_window_lifecycle(self):
  self.w.start(self.c,1,8);a=self.w.register(bytes.fromhex("02"*32),200);b=self.w.register(bytes.fromhex("03"*32),100);c=self.w.register(bytes.fromhex("01"*32),300)
  x=self.w.evaluate_and_close();self.assertEqual([r.record_id for r in x.records],[b.record_id,a.record_id,c.record_id]);self.assertIsNotNone(self.w.verify(x));self.assertEqual(self.w.phase,WindowPhase.VERIFIED)
 def test_record_only_while_running(self):
  with self.assertRaises(WindowError):self.w.register(bytes(32))
  self.w.start(self.c,1,2);self.w.evaluate_and_close()
  with self.assertRaises(WindowError):self.w.register(bytes(32))
 def test_no_iteration_marker_is_created(self):
  self.w.start(self.c,1,2);r=self.w.register(bytes(32));self.assertFalse(hasattr(r,"iteration_index"));self.assertFalse(hasattr(r,"iteration_state_digest"))
 def test_wrong_candidate_rejected(self):
  self.w.start(self.c,1,2);x=self.w.evaluate_and_close();bad=type(x)(2,x.challenge,x.result,x.records);self.assertIsNone(self.w.verify(bad));self.assertEqual(self.w.phase,WindowPhase.CLOSED)

if __name__=="__main__":unittest.main(verbosity=2)
