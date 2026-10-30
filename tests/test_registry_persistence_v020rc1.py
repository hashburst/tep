import sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
from hashburst_tep.encoding import dumps
from hashburst_tep.identity import PeerIdentity,LegacyBinding
from hashburst_tep.identity_binding import BindingStatement,SignedBinding
from hashburst_tep.registry import IdentityRegistry,RegistryError
from hashburst_tep.registry_persistence import registry_bytes,load_registry_bytes,save_registry_atomic,load_registry

def pub(k):return k.public_key().public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw)
def binding(net,seq,node,peer,b):
 k=Ed25519PrivateKey.generate();i=PeerIdentity(pub(k),bytes([b])*32);l=LegacyBinding(i.identity_id(),node,peer,i.transport_public_key);s=BindingStatement(net,seq,i,l);return i,SignedBinding(s,k.sign(s.message()))
class PersistenceTests(unittest.TestCase):
 def setUp(self):
  self.net=bytes.fromhex("61"*32);self.r=IdentityRegistry(self.net);self.i1,self.b1=binding(self.net,0,"node-b","peer-b",1);self.i2,self.b2=binding(self.net,0,"node-a","peer-a",2);self.r.bootstrap(self.b1);self.r.bootstrap(self.b2)
 def test_roundtrip_rebuilds_verified_indexes_and_is_deterministic(self):
  data=registry_bytes(self.r);r2=load_registry_bytes(data);self.assertEqual(registry_bytes(r2),data);self.assertIsNotNone(r2.by_identity(self.i1.identity_id()));self.assertIsNotNone(r2.by_node_id("node-a"))
 def test_tampered_signature_fails_closed(self):
  data=registry_bytes(self.r);v=__import__("hashburst_tep.encoding",fromlist=["loads"]).loads(data);v[2][0][5]=bytes([v[2][0][5][0]^1])+v[2][0][5][1:]
  with self.assertRaises(RegistryError):load_registry_bytes(dumps(v))
 def test_duplicate_index_document_fails_closed(self):
  v=__import__("hashburst_tep.encoding",fromlist=["loads"]).loads(registry_bytes(self.r));v[2].append(v[2][0])
  with self.assertRaises(RegistryError):load_registry_bytes(dumps(v))
 def test_atomic_save_and_restart_recovery(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"registry.cbor";written=save_registry_atomic(p,self.r);r2=load_registry(p);self.assertEqual(p.read_bytes(),written);self.assertEqual(registry_bytes(r2),written)
 def test_failed_replace_preserves_previous_registry(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"registry.cbor";old=save_registry_atomic(p,self.r)
   _,b3=binding(self.net,0,"node-c","peer-c",3);self.r.bootstrap(b3)
   def fail():raise RuntimeError("injected pre-replace failure")
   with self.assertRaises(RuntimeError):save_registry_atomic(p,self.r,before_replace=fail)
   self.assertEqual(p.read_bytes(),old);self.assertFalse(p.with_name(p.name+".tmp").exists());self.assertEqual(registry_bytes(load_registry(p)),old)

if __name__=="__main__":unittest.main(verbosity=2)
