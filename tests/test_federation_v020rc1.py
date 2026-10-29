import sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
from hashburst_tep.federation import Validator,ValidatorSet,FinalityVote,QuorumCertificate,verify_qc
from hashburst_tep.finalizer import finalize_verified_block
from hashburst_tep.block import AcceptedBlock
from hashburst_tep.recovery import load_finalized

def pub(k):return k.public_key().public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw)

class FederationTests(unittest.TestCase):
 def setUp(self):
  self.keys=[Ed25519PrivateKey.generate() for _ in range(4)]
  self.vals=tuple(Validator(bytes([i+1])*32,pub(k)) for i,k in enumerate(self.keys));self.vs=ValidatorSet(7,self.vals)
  self.net=bytes.fromhex("aa"*32);self.bid=bytes.fromhex("bb"*32)
 def qc(self,indexes=(0,1,2),count=9,bid=None):
  bid=self.bid if bid is None else bid
  shell=QuorumCertificate(self.vs.version,self.vs.digest(),self.net,count,bid,())
  votes=tuple(FinalityVote(self.vals[i].validator_id,self.keys[i].sign(shell.message())) for i in indexes)
  return QuorumCertificate(self.vs.version,self.vs.digest(),self.net,count,bid,votes)
 def test_threshold_four_requires_three(self):
  self.assertEqual(self.vs.threshold(),3);self.assertTrue(verify_qc(self.qc(),self.vs));self.assertFalse(verify_qc(self.qc((0,1)),self.vs))
 def test_duplicate_vote_rejected(self):
  q=self.qc((0,1,2));bad=QuorumCertificate(q.validator_set_version,q.validator_set_digest,q.network_id,q.count,q.block_id,(q.votes[0],q.votes[0],q.votes[2]));self.assertFalse(verify_qc(bad,self.vs))
 def test_wrong_block_and_signature_rejected(self):
  self.assertFalse(verify_qc(self.qc(bid=bytes.fromhex("cc"*32)),self.vs))
  q=self.qc();v=list(q.votes);v[0]=FinalityVote(v[0].validator_id,bytes(64));bad=QuorumCertificate(q.validator_set_version,q.validator_set_digest,q.network_id,q.count,q.block_id,tuple(v));self.assertFalse(verify_qc(bad,self.vs))
 def test_duplicate_validator_identity_or_key_rejected(self):
  with self.assertRaises(ValueError):ValidatorSet(1,(self.vals[0],self.vals[0])).digest()
  with self.assertRaises(ValueError):ValidatorSet(1,(self.vals[0],Validator(bytes.fromhex("ff"*32),self.vals[0].public_key))).digest()
 def test_finalizer_requires_valid_qc(self):
  block=AcceptedBlock((1,9,bytes(32),bytes(32),bytes.fromhex("dd"*32),1,bytes.fromhex("11"*32),bytes(32)),(),b"",self.bid,bytes.fromhex("dd"*32))
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"f.chk"
   with self.assertRaises(ValueError):finalize_verified_block(p,network_id=self.net,block=block,vdf_params_hash=bytes.fromhex("11"*32),validator_set=self.vs,qc=self.qc((0,1)))
   self.assertFalse(p.exists())
   state=finalize_verified_block(p,network_id=self.net,block=block,vdf_params_hash=bytes.fromhex("11"*32),validator_set=self.vs,qc=self.qc())
   self.assertEqual(load_finalized(p).checkpoint,state.checkpoint);self.assertEqual(state.checkpoint.validator_set_version,7)

if __name__=="__main__":unittest.main(verbosity=2)
