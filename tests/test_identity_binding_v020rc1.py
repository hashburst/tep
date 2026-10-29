import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
from hashburst_tep.identity import PeerIdentity,LegacyBinding
from hashburst_tep.identity_binding import BindingStatement,SignedBinding,RotationStatement,AuthorizedRotation,verify_signed_binding,verify_rotation

def pub(k):return k.public_key().public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw)

class BindingTests(unittest.TestCase):
 def setUp(self):
  self.net=bytes.fromhex("31"*32);self.oldk=Ed25519PrivateKey.generate();self.newk=Ed25519PrivateKey.generate()
  self.old=PeerIdentity(pub(self.oldk),bytes.fromhex("41"*32));self.new=PeerIdentity(pub(self.newk),bytes.fromhex("42"*32))
 def signed(self,identity,key,seq,node="node-a",peer="peer-a"):
  legacy=LegacyBinding(identity.identity_id(),node,peer,identity.transport_public_key)
  s=BindingStatement(self.net,seq,identity,legacy);return SignedBinding(s,key.sign(s.message()))
 def test_binding_requires_current_identity_signature(self):
  b=self.signed(self.old,self.oldk,7);self.assertTrue(verify_signed_binding(b))
  self.assertFalse(verify_signed_binding(SignedBinding(b.statement,self.newk.sign(b.statement.message()))))
 def test_substitution_of_legacy_identifiers_breaks_signature(self):
  b=self.signed(self.old,self.oldk,7)
  altered=self.signed(self.old,self.oldk,7,node="node-b")
  self.assertNotEqual(b.statement.digest(),altered.statement.digest())
  forged=SignedBinding(altered.statement,b.signature);self.assertFalse(verify_signed_binding(forged))
 def test_rotation_requires_old_continuity_and_new_binding_signatures(self):
  nb=self.signed(self.new,self.newk,8,"node-new","peer-new")
  rs=RotationStatement(self.net,8,self.old.identity_id(),nb.statement.digest())
  r=AuthorizedRotation(nb,rs,self.oldk.sign(rs.message()))
  self.assertTrue(verify_rotation(r,self.old,7))
  self.assertFalse(verify_rotation(AuthorizedRotation(nb,rs,self.newk.sign(rs.message())),self.old,7))
 def test_rotation_rejects_replay_skip_and_network_substitution(self):
  nb=self.signed(self.new,self.newk,8);rs=RotationStatement(self.net,8,self.old.identity_id(),nb.statement.digest());r=AuthorizedRotation(nb,rs,self.oldk.sign(rs.message()))
  self.assertFalse(verify_rotation(r,self.old,8))
  skip=self.signed(self.new,self.newk,9);sr=RotationStatement(self.net,9,self.old.identity_id(),skip.statement.digest());self.assertFalse(verify_rotation(AuthorizedRotation(skip,sr,self.oldk.sign(sr.message())),self.old,7))
  wrong=RotationStatement(bytes.fromhex("99"*32),8,self.old.identity_id(),nb.statement.digest());self.assertFalse(verify_rotation(AuthorizedRotation(nb,wrong,self.oldk.sign(wrong.message())),self.old,7))

if __name__=="__main__":unittest.main(verbosity=2)
