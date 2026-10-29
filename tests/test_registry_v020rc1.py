import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
from hashburst_tep.identity import PeerIdentity,LegacyBinding
from hashburst_tep.identity_binding import BindingStatement,SignedBinding,RotationStatement,AuthorizedRotation
from hashburst_tep.registry import IdentityRegistry,RegistryError

def pub(k):return k.public_key().public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw)
class RegistryTests(unittest.TestCase):
 def setUp(self):self.net=bytes.fromhex("51"*32);self.r=IdentityRegistry(self.net)
 def make(self,seq,node,peer,transport_byte):
  k=Ed25519PrivateKey.generate();i=PeerIdentity(pub(k),bytes([transport_byte])*32);l=LegacyBinding(i.identity_id(),node,peer,i.transport_public_key);s=BindingStatement(self.net,seq,i,l);return k,i,SignedBinding(s,k.sign(s.message()))
 def test_bootstrap_and_bidirectional_resolution(self):
  k,i,b=self.make(0,"node-a","peer-a",1);e=self.r.bootstrap(b)
  self.assertIs(self.r.by_identity(i.identity_id()),e);self.assertIs(self.r.by_address(e.address),e);self.assertIs(self.r.by_node_id("node-a"),e);self.assertIs(self.r.by_peer_id("peer-a"),e)
 def test_replay_and_duplicate_indexes_rejected(self):
  k,i,b=self.make(0,"node-a","peer-a",1);self.r.bootstrap(b)
  with self.assertRaises(RegistryError):self.r.bootstrap(b)
  _,_,dupnode=self.make(0,"node-a","peer-b",2)
  with self.assertRaises(RegistryError):self.r.bootstrap(dupnode)
  _,_,duppeer=self.make(0,"node-b","peer-a",3)
  with self.assertRaises(RegistryError):self.r.bootstrap(duppeer)
 def test_authorized_rotation_replaces_indexes_atomically_in_memory(self):
  ok,oi,ob=self.make(4,"node-old","peer-old",4);self.r.bootstrap(ob)
  nk,ni,nb=self.make(5,"node-new","peer-new",5);rs=RotationStatement(self.net,5,oi.identity_id(),nb.statement.digest());rot=AuthorizedRotation(nb,rs,ok.sign(rs.message()));e=self.r.rotate(rot)
  self.assertIsNone(self.r.by_identity(oi.identity_id()));self.assertIsNone(self.r.by_node_id("node-old"));self.assertIs(self.r.by_identity(ni.identity_id()),e);self.assertIs(self.r.by_node_id("node-new"),e)
 def test_rotation_replay_and_substitution_rejected_without_state_change(self):
  ok,oi,ob=self.make(4,"node-old","peer-old",4);old=self.r.bootstrap(ob)
  nk,ni,nb=self.make(5,"node-new","peer-new",5);rs=RotationStatement(self.net,5,oi.identity_id(),nb.statement.digest());bad=AuthorizedRotation(nb,rs,nk.sign(rs.message()))
  with self.assertRaises(RegistryError):self.r.rotate(bad)
  self.assertIs(self.r.by_identity(oi.identity_id()),old);self.assertIsNone(self.r.by_identity(ni.identity_id()))
 def test_wrong_network_binding_rejected(self):
  _,_,b=self.make(0,"node-a","peer-a",1);other=IdentityRegistry(bytes.fromhex("99"*32))
  with self.assertRaises(RegistryError):other.bootstrap(b)

if __name__=="__main__":unittest.main(verbosity=2)
