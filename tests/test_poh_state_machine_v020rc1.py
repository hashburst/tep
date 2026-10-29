import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from hashburst_tep.poh import PoHPhase,PoHStateMachine,PoHStateError
from hashburst_tep.vdf import DeterministicTestVDF,VDFResult

class PoHStateMachineTests(unittest.TestCase):
 def setUp(self):self.a=DeterministicTestVDF();self.s=PoHStateMachine(self.a);self.c=bytes.fromhex("aa"*32)
 def test_adapter_is_reproducible(self):
  a=self.a.evaluate(self.c,8);b=self.a.evaluate(self.c,8);self.assertEqual(a,b);self.assertTrue(self.a.verify(self.c,a))
  self.assertFalse(self.a.verify(self.c,VDFResult(a.output,bytes(32),8)))
 def test_window_bind_close_verify(self):
  self.s.start(self.c,1,8);self.assertEqual(self.s.phase,PoHPhase.EVALUATING)
  self.s.advance(2);r1=self.s.bind_record(bytes.fromhex("22"*32),200)
  self.s.advance(3);r2=self.s.bind_record(bytes.fromhex("11"*32),100)
  self.assertEqual((r1.iteration_index,r2.iteration_index),(2,5))
  cand=self.s.close();self.assertEqual(self.s.phase,PoHPhase.CLOSED);self.assertEqual([r.record_id for r in cand.records],[r1.record_id,r2.record_id])
  self.assertTrue(self.s.verify(cand));self.assertEqual(self.s.phase,PoHPhase.VERIFIED);self.s.reset_after_verified();self.assertEqual(self.s.phase,PoHPhase.IDLE)
 def test_record_requires_completed_iteration(self):
  self.s.start(self.c,1,4)
  with self.assertRaises(PoHStateError):self.s.bind_record(bytes(32))
 def test_closed_window_rejects_record(self):
  self.s.start(self.c,1,2);self.s.advance();self.s.close()
  with self.assertRaises(PoHStateError):self.s.bind_record(bytes(32))
 def test_same_iteration_order(self):
  self.s.start(self.c,1,2);self.s.advance()
  later=self.s.bind_record(bytes.fromhex("02"*32),200);earlier=self.s.bind_record(bytes.fromhex("03"*32),100);untimed=self.s.bind_record(bytes.fromhex("01"*32),None)
  cand=self.s.close();self.assertEqual([r.record_id for r in cand.records],[earlier.record_id,later.record_id,untimed.record_id])
 def test_wrong_candidate_not_verified(self):
  self.s.start(self.c,1,2);self.s.advance();cand=self.s.close()
  bad=type(cand)(2,cand.challenge,cand.result,cand.records);self.assertFalse(self.s.verify(bad));self.assertEqual(self.s.phase,PoHPhase.CLOSED)

if __name__=="__main__":unittest.main(verbosity=2)
