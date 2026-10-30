import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from hashburst_tep.block import assemble_verified_block
from hashburst_tep.poh import EvaluationWindow,VerifiedWindowCandidate,WindowError
from hashburst_tep.vdf import DeterministicTestVDF

class ReleaseHardeningTests(unittest.TestCase):
 def test_verify_returns_sealed_candidate_and_raw_candidate_cannot_assemble(self):
  w=EvaluationWindow(DeterministicTestVDF());challenge=bytes.fromhex("11"*32);w.start(challenge,1,4);rid=bytes.fromhex("22"*32);w.register(rid)
  raw=w.evaluate_and_close();verified=w.verify(raw);self.assertIsInstance(verified,VerifiedWindowCandidate)
  record=([2,bytes(32),bytes(32),bytes(32),1,bytes(32),None,bytes(32)],rid,None)
  with self.assertRaises(ValueError):assemble_verified_block(verified=raw,count=1,previous_h=bytes(32),previous_block_id=bytes(32),vdf_suite=1,vdf_params_hash=bytes(32),records=[record])
 def test_assembly_rejects_record_set_or_order_not_verified(self):
  w=EvaluationWindow(DeterministicTestVDF());challenge=bytes.fromhex("11"*32);w.start(challenge,1,4);a=bytes.fromhex("22"*32);b=bytes.fromhex("33"*32);w.register(a);w.register(b)
  v=w.verify(w.evaluate_and_close());ra=([2,bytes(32),bytes(32),bytes(32),1,bytes(32),None,bytes(32)],a,None);rb=([2,bytes(32),bytes(32),bytes(32),2,bytes(32),None,bytes(32)],b,None)
  with self.assertRaises(ValueError):assemble_verified_block(verified=v,count=1,previous_h=bytes(32),previous_block_id=bytes(32),vdf_suite=1,vdf_params_hash=bytes(32),records=[rb,ra])
 def test_tsa_profile_rejects_mixed_window(self):
  w=EvaluationWindow(DeterministicTestVDF());w.start(bytes.fromhex("11"*32),1,4);w.register(bytes.fromhex("22"*32),100)
  with self.assertRaises(WindowError):w.register(bytes.fromhex("33"*32),None)
 def test_non_tsa_and_all_tsa_profiles_are_each_valid(self):
  for timed in (False,True):
   w=EvaluationWindow(DeterministicTestVDF());w.start(bytes.fromhex("11"*32),1,4);w.register(bytes.fromhex("22"*32),100 if timed else None);w.register(bytes.fromhex("33"*32),200 if timed else None);self.assertIsInstance(w.verify(w.evaluate_and_close()),VerifiedWindowCandidate)

if __name__=="__main__":unittest.main(verbosity=2)
