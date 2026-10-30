import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from hashburst_tep.federation import Validator
from hashburst_tep.federation_v03 import *

class FederationV03Tests(unittest.TestCase):
 def v(self,n):return Validator(bytes([n])*32,bytes([n+10])*32)
 def state(self):
  return FederationState(bytes.fromhex("aa"*32),3,tuple(Member(self.v(i),ACTIVE) for i in range(1,5)))
 def test_active_set_and_threshold(self):
  s=self.state();self.assertEqual(s.active_validator_set().threshold(),3);self.assertEqual(s.active_validator_set().version,3)
 def test_membership_transition_versions_state(self):
  s=self.state();p=MembershipProposal(s.federation_id,3,self.v(1),SUSPENDED);n=apply_membership(s,p)
  self.assertEqual(n.version,4);self.assertEqual(len(n.active_validator_set().validators),3)
 def test_stale_membership_proposal_rejected(self):
  s=self.state();p=MembershipProposal(s.federation_id,2,self.v(1),SUSPENDED)
  with self.assertRaises(ValueError):apply_membership(s,p)
 def test_revocation_terminal(self):
  s=self.state();r=apply_membership(s,MembershipProposal(s.federation_id,3,self.v(1),REVOKED))
  with self.assertRaises(ValueError):apply_membership(r,MembershipProposal(r.federation_id,4,self.v(1),ACTIVE))
 def test_key_replacement_rejected(self):
  s=self.state();changed=Validator(self.v(1).validator_id,bytes.fromhex("ff"*32))
  with self.assertRaises(ValueError):apply_membership(s,MembershipProposal(s.federation_id,3,changed,SUSPENDED))
 def test_new_member_activation(self):
  s=self.state();n=apply_membership(s,MembershipProposal(s.federation_id,3,self.v(9),ACTIVE))
  self.assertEqual(len(n.active_validator_set().validators),5)
 def test_sovereignty_permissions_and_digest(self):
  a,b,c=(bytes([x])*32 for x in (1,2,3));p=SovereigntyPolicy(bytes.fromhex("ee"*32),7,(a,),(b,),(c,))
  self.assertTrue(p.permits_storage(a));self.assertFalse(p.permits_storage(b));self.assertEqual(len(p.digest()),32)
 def test_sovereignty_rejects_duplicate_domains(self):
  a=bytes.fromhex("01"*32);p=SovereigntyPolicy(bytes.fromhex("ee"*32),1,(a,a),(),())
  with self.assertRaises(ValueError):p.digest()

 def test_equivocation_tracker(self):
  t=EquivocationTracker();k=VoteKey(bytes.fromhex("aa"*32),3,9,self.v(1).validator_id);a=bytes.fromhex("11"*32);b=bytes.fromhex("22"*32)
  self.assertTrue(t.observe(k,a));self.assertFalse(t.observe(k,a))
  with self.assertRaises(ValueError):t.observe(k,b)
 def test_partition_quorum(self):
  self.assertTrue(partition_has_quorum(7,5));self.assertFalse(partition_has_quorum(7,4));self.assertFalse(partition_has_quorum(4,2))
 def test_recovery_cursor_requires_forward_progress(self):
  c=RecoveryCursor(bytes.fromhex("aa"*32),3,10,bytes.fromhex("bb"*32))
  self.assertTrue(c.accepts_next(3,11));self.assertTrue(c.accepts_next(4,11));self.assertFalse(c.accepts_next(2,11));self.assertFalse(c.accepts_next(3,10))

if __name__=="__main__":unittest.main(verbosity=2)
