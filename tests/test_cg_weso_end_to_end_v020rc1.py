import sys,tempfile,time,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
from hashburst_tep.genesis import Genesis
from hashburst_tep.records_v2 import WindowRecordCore,ledger_record
from hashburst_tep.federation import Validator,ValidatorSet,FinalityVote
from hashburst_tep.orchestrator import PreviousLedgerState,LedgerOrchestrator
from hashburst_tep.recovery import load_finalized
from hashburst_tep.vdf import CGWesoV1

def pub(k):return k.public_key().public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw)

class CGWesoEndToEndTests(unittest.TestCase):
 def setUp(self):
  self.net=bytes.fromhex("a5"*32);self.vp=bytes.fromhex("11"*32);self.gen=Genesis(self.net,1,1,self.vp)
  self.keys=[Ed25519PrivateKey.generate() for _ in range(4)]
  self.vals=tuple(Validator(bytes([i+1])*32,pub(k)) for i,k in enumerate(self.keys));self.vs=ValidatorSet(11,self.vals)
  self.o=LedgerOrchestrator(network_id=self.net,vdf_params_hash=self.vp,vdf_suite=1,iterations=4096,adapter=CGWesoV1(),validator_set=self.vs)
  self.prev=PreviousLedgerState(0,self.gen.h0(),bytes.fromhex("22"*32))
 def record(self):
  c=WindowRecordCore(bytes.fromhex("31"*32),bytes.fromhex("32"*32),bytes.fromhex("33"*32),1,self.prev.block_id,None,bytes.fromhex("44"*32))
  return ledger_record(c,b"synthetic-protection")
 def votes(self,p,indexes=(0,1,2)):
  return tuple(FinalityVote(self.vals[i].validator_id,self.keys[i].sign(p.vote_message)) for i in indexes)
 def test_real_cg_weso_finalize_and_recover(self):
  t0=time.perf_counter();p=self.o.prepare(self.prev,[self.record()]);elapsed=time.perf_counter()-t0
  self.assertEqual(len(p.block.proof),100);self.assertEqual(p.block.header[1],1);self.assertGreater(elapsed,0)
  with tempfile.TemporaryDirectory() as d:
   path=Path(d)/"final.chk";state=self.o.finalize(path,p,self.votes(p));loaded=load_finalized(path)
   self.assertEqual(loaded.checkpoint.block_id,p.block.block_id);self.assertEqual(loaded.checkpoint,state.checkpoint)
 def test_real_cg_weso_insufficient_quorum_never_persists(self):
  p=self.o.prepare(self.prev,[self.record()])
  with tempfile.TemporaryDirectory() as d:
   path=Path(d)/"final.chk"
   with self.assertRaises(ValueError):self.o.finalize(path,p,self.votes(p,(0,1)))
   self.assertFalse(path.exists())

if __name__=="__main__":unittest.main(verbosity=2)
