import sys,unittest,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding,PublicFormat
from hashburst_tep.federation import Validator
from hashburst_tep.governance import *

class GovernanceProductionTests(unittest.TestCase):
 def setUp(self):
  self.keys=[Ed25519PrivateKey.generate() for _ in range(5)]
  self.ids=[bytes([i])*32 for i in range(1,6)]
  self.pks=[k.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw) for k in self.keys]
  self.fid=b"F"*32
  self.state=GovernanceState(self.fid,1,tuple(GovernanceMember(self.ids[i],self.pks[i],ACTIVE if i<4 else ENROLLED) for i in range(5)))
 def votes(self,p,s,count):
  msg=p.vote_message(s);keys={self.ids[i]:self.keys[i] for i in range(5)}
  return tuple(GovernanceVote(v.validator_id,keys[v.validator_id].sign(msg)) for v in s.ordered()[:count])
 def proposal(self,state,index,to_state,new_key=None):
  m={x.validator_id:x for x in state.ordered()}[self.ids[index]]
  return GovernanceProposal(self.fid,state.version,m.validator_id,m.public_key,new_key or m.public_key,m.state,to_state,bytes([state.version])*32)
 def test_two_of_four_rejected_three_of_four_accepted(self):
  s=self.state.active_validator_set();p=self.proposal(self.state,4,CANDIDATE)
  with self.assertRaises(ValueError):apply_governance(self.state,p,self.votes(p,s,2),s)
  n=apply_governance(self.state,p,self.votes(p,s,3),s);self.assertEqual({x.validator_id:x.state for x in n.members}[self.ids[4]],CANDIDATE)
 def test_full_lifecycle(self):
  state=self.state
  for target in (CANDIDATE,PENDING_ACTIVATION,ACTIVE,SUSPENDED):
   s=state.active_validator_set();p=self.proposal(state,4,target);state=apply_governance(state,p,self.votes(p,s,3),s)
  new=Ed25519PrivateKey.generate().public_key().public_bytes(Encoding.Raw,PublicFormat.Raw);s=state.active_validator_set();p=self.proposal(state,4,PENDING_ACTIVATION,new);state=apply_governance(state,p,self.votes(p,s,3),s)
  self.assertEqual({x.validator_id:x.public_key for x in state.members}[self.ids[4]],new)
  s=state.active_validator_set();p=self.proposal(state,4,ACTIVE);state=apply_governance(state,p,self.votes(p,s,3),s)
  s=state.active_validator_set();p=self.proposal(state,4,REVOKED);state=apply_governance(state,p,self.votes(p,s,3),s)
  self.assertEqual({x.validator_id:x.state for x in state.members}[self.ids[4]],REVOKED)
 def test_old_set_rejected_after_version_change(self):
  old=self.state.active_validator_set();p=self.proposal(self.state,4,CANDIDATE);n=apply_governance(self.state,p,self.votes(p,old,3),old)
  p2=self.proposal(n,4,PENDING_ACTIVATION)
  with self.assertRaises(ValueError):apply_governance(n,p2,self.votes(p2,old,3),old)
 def test_rotation_requires_suspension(self):
  s=self.state.active_validator_set();new=b"Z"*32;p=self.proposal(self.state,0,SUSPENDED);n=apply_governance(self.state,p,self.votes(p,s,3),s)
  ns=n.active_validator_set();rot=self.proposal(n,0,PENDING_ACTIVATION,new);r=apply_governance(n,rot,self.votes(rot,ns,3),ns)
  self.assertEqual({x.validator_id:x.public_key for x in r.members}[self.ids[0]],new)
 def test_persistent_restart_and_replay(self):
  with tempfile.TemporaryDirectory() as d:
   path=Path(d)/"registry.json";r=PersistentGovernanceRegistry(path);r.initialize(self.state)
   s=r.state.active_validator_set();p=self.proposal(r.state,4,CANDIDATE);r.apply(p,self.votes(p,s,3),s)
   r2=PersistentGovernanceRegistry(path);self.assertEqual(r2.state.digest(),r.state.digest())
   with self.assertRaises(ValueError):r2.apply(p,self.votes(p,s,3),s)

if __name__=="__main__":unittest.main(verbosity=2)
