import sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
from hashburst_tep.cose_sign1 import sign1_ed25519
from hashburst_tep.genesis import Genesis
from hashburst_tep.records_v2 import WindowRecordCore,ledger_record
from hashburst_tep.federation import Validator,ValidatorSet,FinalityVote
from hashburst_tep.orchestrator import PreviousLedgerState,LedgerOrchestrator
from hashburst_tep.recovery import load_finalized
from hashburst_tep.vdf import DeterministicTestVDF

def pub(k):return k.public_key().public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw)

class OrchestratorTests(unittest.TestCase):
 def setUp(self):
  self.net=bytes.fromhex("10"*32);self.vp=bytes.fromhex("11"*32);self.gen=Genesis(self.net,1,1,self.vp)
  self.keys=[Ed25519PrivateKey.generate() for _ in range(4)]
  self.record_key=Ed25519PrivateKey.generate()
  self.vals=tuple(Validator(bytes([i+1])*32,pub(k)) for i,k in enumerate(self.keys));self.vs=ValidatorSet(1,self.vals)
  self.o=LedgerOrchestrator(network_id=self.net,vdf_params_hash=self.vp,vdf_suite=1,iterations=8,adapter=DeterministicTestVDF(),validator_set=self.vs)
  self.prev=PreviousLedgerState(0,self.gen.h0(),bytes.fromhex("22"*32))
 def rec(self,n,time=None):
  c=WindowRecordCore(bytes.fromhex("31"*32),bytes.fromhex("32"*32),bytes([n])*32,n,self.prev.block_id,time,bytes([n+10])*32)
  return ledger_record(c,sign1_ed25519(c.encode(),self.record_key))
 def votes(self,p,indexes=(0,1,2)):
  return tuple(FinalityVote(self.vals[i].validator_id,self.keys[i].sign(p.vote_message)) for i in indexes)
 def test_end_to_end_prepare_vote_finalize_recover(self):
  p=self.o.prepare(self.prev,[self.rec(1,200),self.rec(2,100)])
  self.assertEqual(p.block.header[1],1)
  with tempfile.TemporaryDirectory() as d:
   path=Path(d)/"final.chk";state=self.o.finalize(path,p,self.votes(p));loaded=load_finalized(path)
   self.assertEqual(loaded.checkpoint,state.checkpoint);self.assertEqual(loaded.checkpoint.block_id,p.block.block_id)
 def test_insufficient_votes_never_persist(self):
  p=self.o.prepare(self.prev,[self.rec(1)])
  with tempfile.TemporaryDirectory() as d:
   path=Path(d)/"final.chk"
   with self.assertRaises(ValueError):self.o.finalize(path,p,self.votes(p,(0,1)))
   self.assertFalse(path.exists())
 def test_signature_for_other_prepared_block_rejected(self):
  p1=self.o.prepare(self.prev,[self.rec(1)])
  p2=self.o.prepare(self.prev,[self.rec(2)])
  with tempfile.TemporaryDirectory() as d:
   path=Path(d)/"final.chk"
   with self.assertRaises(ValueError):self.o.finalize(path,p2,self.votes(p1))
   self.assertFalse(path.exists())
 def test_duplicate_record_rejected_before_vdf(self):
  r=self.rec(1)
  with self.assertRaises(ValueError):self.o.prepare(self.prev,[r,r])

if __name__=="__main__":unittest.main(verbosity=2)
