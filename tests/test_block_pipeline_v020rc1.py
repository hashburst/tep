import sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from hashburst_tep.block import assemble_verified_block
from hashburst_tep.checkpoint import Checkpoint
from hashburst_tep.cose_sign1 import sign1_ed25519
from hashburst_tep.genesis import Genesis
from hashburst_tep.ledger import poh_input
from hashburst_tep.poh import EvaluationWindow
from hashburst_tep.records_v2 import WindowRecordCore,ledger_record
from hashburst_tep.recovery import persist_finalized
from hashburst_tep.vdf import DeterministicTestVDF

class PipelineTests(unittest.TestCase):
 def setUp(self):
  self.net=bytes(32);self.vp=bytes.fromhex("11"*32);self.prev=bytes.fromhex("22"*32);self.g=Genesis(self.net,1,1,self.vp);self.challenge=poh_input(self.net,1,self.g.h0(),self.prev,self.vp);self.signer=Ed25519PrivateKey.generate()
 def _record(self,tag,seq,time=None):
  c=WindowRecordCore(bytes.fromhex("33"*32),bytes.fromhex("44"*32),bytes.fromhex(tag*32),seq,self.prev,time,bytes.fromhex("77"*32));return ledger_record(c,sign1_ed25519(c.encode(),self.signer))
 def test_b0_to_b1_candidate_and_checkpoint(self):
  w=EvaluationWindow(DeterministicTestVDF());w.start(self.challenge,1,8)
  r1=self._record("55",1,200);r2=self._record("66",2,100);w.register(r1[1],200);w.register(r2[1],100)
  cand=w.evaluate_and_close();self.assertTrue(w.verify(cand))
  by_id={r[1]:r for r in (r1,r2)};ordered=[by_id[x.record_id] for x in cand.records]
  b=assemble_verified_block(count=1,previous_h=self.g.h0(),previous_block_id=self.prev,challenge=self.challenge,result=cand.result,vdf_suite=1,vdf_params_hash=self.vp,records=ordered)
  self.assertEqual(b.header[1],1);self.assertEqual(len(b.block_id),32);self.assertEqual(len(b.h),32)
  cp=Checkpoint(self.net,1,b.h,b.block_id,self.vp,1,bytes.fromhex("88"*32))
  with tempfile.TemporaryDirectory() as d:
   s=persist_finalized(Path(d)/"finalized.chk",cp);self.assertEqual(s.checkpoint_id,cp.checkpoint_id());self.assertTrue((Path(d)/"finalized.chk").exists())
 def test_unverified_candidate_not_pipeline_input(self):
  w=EvaluationWindow(DeterministicTestVDF());w.start(self.challenge,1,2);cand=w.evaluate_and_close();self.assertEqual(w.phase.value,"closed")
  self.assertNotEqual(w.phase.value,"verified")
 def test_record_v2_has_no_synthetic_iteration_fields(self):
  r=self._record("55",1);self.assertEqual(r[0][0],2);self.assertEqual(len(r[0]),8)

if __name__=="__main__":unittest.main(verbosity=2)
