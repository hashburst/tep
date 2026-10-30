import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
from hashburst_tep.identity import PeerIdentity,LegacyBinding
from hashburst_tep.identity_binding import BindingStatement,SignedBinding
from hashburst_tep.registry import IdentityRegistry
from hashburst_tep.discovery import ReachabilityStatement,SignedReachability,ReachabilityTable,DiscoveryError

def pub(k):return k.public_key().public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw)
class DiscoveryTests(unittest.TestCase):
 def setUp(self):
  self.net=bytes.fromhex("71"*32);self.k=Ed25519PrivateKey.generate();self.i=PeerIdentity(pub(self.k),bytes.fromhex("72"*32));l=LegacyBinding(self.i.identity_id(),"node-a","peer-a",self.i.transport_public_key);s=BindingStatement(self.net,0,self.i,l);self.r=IdentityRegistry(self.net);self.e=self.r.bootstrap(SignedBinding(s,self.k.sign(s.message())));self.t=ReachabilityTable(self.r)
 def signed(self,seq,host="192.0.2.10",port=47777,key=None,iid=None,net=None):
  s=ReachabilityStatement(net or self.net,iid or self.i.identity_id(),seq,host,port);k=key or self.k;return SignedReachability(s,k.sign(s.message()))
 def test_authenticated_endpoint_update_and_all_resolution_paths(self):
  e=self.t.update(self.signed(1));self.assertEqual((e.host,e.port),("192.0.2.10",47777));self.assertIs(self.t.resolve_identity(self.i.identity_id()),e);self.assertIs(self.t.resolve_address(self.e.address),e);self.assertIs(self.t.resolve_node_id("node-a"),e);self.assertIs(self.t.resolve_peer_id("peer-a"),e)
 def test_endpoint_is_mutable_but_identity_is_stable(self):
  self.t.update(self.signed(1));e=self.t.update(self.signed(2,"198.51.100.20",47777));self.assertEqual(e.host,"198.51.100.20");self.assertEqual(self.r.by_identity(self.i.identity_id()).address,self.e.address)
 def test_replay_and_stale_updates_rejected(self):
  self.t.update(self.signed(4))
  for seq in (4,3):
   with self.assertRaises(DiscoveryError):self.t.update(self.signed(seq))
  self.assertEqual(self.t.resolve_identity(self.i.identity_id()).sequence,4)
 def test_wrong_key_unknown_identity_and_network_rejected(self):
  bad=Ed25519PrivateKey.generate()
  with self.assertRaises(DiscoveryError):self.t.update(self.signed(1,key=bad))
  with self.assertRaises(DiscoveryError):self.t.update(self.signed(1,iid=bytes.fromhex("99"*32)))
  with self.assertRaises(DiscoveryError):self.t.update(self.signed(1,net=bytes.fromhex("98"*32)))
 def test_invalid_endpoint_rejected_without_state_change(self):
  for host,port in (("not-an-ip",47777),("192.0.2.1",0),("192.0.2.1",65536)):
   with self.assertRaises(DiscoveryError):self.t.update(self.signed(1,host,port))
  self.assertIsNone(self.t.resolve_identity(self.i.identity_id()))

if __name__=="__main__":unittest.main(verbosity=2)
