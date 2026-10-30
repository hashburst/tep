import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
from hashburst_tep.identity import PeerIdentity,LegacyBinding
from hashburst_tep.identity_binding import BindingStatement,SignedBinding
from hashburst_tep.registry import IdentityRegistry
from hashburst_tep.discovery import DiscoveryError
from hashburst_tep.legacy_v22_adapter import LegacyAuthenticatedEndpoint,LegacyV22ReachabilityAdapter

def pub(k):return k.public_key().public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw)
class AdapterTests(unittest.TestCase):
 def setUp(self):
  net=bytes.fromhex("81"*32);k=Ed25519PrivateKey.generate();self.i=PeerIdentity(pub(k),bytes.fromhex("82"*32));l=LegacyBinding(self.i.identity_id(),"node-production-long","12D3KooW-peer",self.i.transport_public_key);s=BindingStatement(net,0,self.i,l);r=IdentityRegistry(net);r.bootstrap(SignedBinding(s,k.sign(s.message())));self.a=LegacyV22ReachabilityAdapter(r)
 def ev(self,**kw):
  d=dict(node_id="node-production-long",peer_id="12D3KooW-peer",x25519_public_key=self.i.transport_public_key,host="192.0.2.40",port=47777,authenticated=True);d.update(kw);return LegacyAuthenticatedEndpoint(**d)
 def test_authenticated_registered_v22_event_resolves_canonical_identity(self):
  iid,h,p=self.a.resolve_authenticated_event(self.ev());self.assertEqual(iid,self.i.identity_id());self.assertEqual((h,p),("192.0.2.40",47777))
 def test_unauthenticated_legacy_heartbeat_cannot_promote_reachability(self):
  with self.assertRaises(DiscoveryError):self.a.resolve_authenticated_event(self.ev(authenticated=False))
 def test_peer_id_and_x25519_substitution_rejected(self):
  with self.assertRaises(DiscoveryError):self.a.resolve_authenticated_event(self.ev(peer_id="attacker"))
  with self.assertRaises(DiscoveryError):self.a.resolve_authenticated_event(self.ev(x25519_public_key=bytes.fromhex("99"*32)))
 def test_unknown_node_and_invalid_endpoint_rejected(self):
  with self.assertRaises(DiscoveryError):self.a.resolve_authenticated_event(self.ev(node_id="unknown"))
  with self.assertRaises(DiscoveryError):self.a.resolve_authenticated_event(self.ev(host="not-an-ip"))
 def test_legacy_wire_truncation_is_not_used_as_canonical_identity(self):
  with self.assertRaises(DiscoveryError):self.a.resolve_authenticated_event(self.ev(node_id="node-production-l"))

if __name__=="__main__":unittest.main(verbosity=2)
