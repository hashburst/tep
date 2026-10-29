import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from hashburst_tep.identity import PeerIdentity,LegacyBinding

class IdentityTests(unittest.TestCase):
 def setUp(self):
  self.i=PeerIdentity(bytes.fromhex("11"*32),bytes.fromhex("22"*32));self.net=bytes.fromhex("33"*32)
 def test_identity_and_address_are_deterministic_and_network_scoped(self):
  self.assertEqual(self.i.identity_id(),self.i.identity_id());self.assertEqual(len(self.i.identity_id()),32);self.assertEqual(len(self.i.ledger_address(self.net)),32)
  self.assertNotEqual(self.i.ledger_address(self.net),self.i.ledger_address(bytes.fromhex("44"*32)))
 def test_signing_and_transport_keys_are_both_identity_bound(self):
  self.assertNotEqual(self.i.identity_id(),PeerIdentity(bytes.fromhex("55"*32),bytes.fromhex("22"*32)).identity_id())
  self.assertNotEqual(self.i.identity_id(),PeerIdentity(bytes.fromhex("11"*32),bytes.fromhex("66"*32)).identity_id())
 def test_legacy_binding_preserves_v22_identifiers_without_equating_them(self):
  b=LegacyBinding(self.i.identity_id(),"hashburst-node-long-name","12D3KooW-example",self.i.transport_public_key)
  self.assertTrue(b.validate_for(self.i));self.assertEqual(b.wire_node_field(),b"hashburst-node-lo")
  self.assertNotEqual(self.i.identity_id(),b.wire_node_field().ljust(32,b"\x00"))
 def test_legacy_binding_rejects_wrong_transport_key(self):
  b=LegacyBinding(self.i.identity_id(),"node-a","peer-a",bytes.fromhex("77"*32));self.assertFalse(b.validate_for(self.i))

if __name__=="__main__":unittest.main(verbosity=2)
