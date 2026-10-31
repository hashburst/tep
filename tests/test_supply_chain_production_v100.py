import sys,tempfile,unittest,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding,PrivateFormat,PublicFormat,NoEncryption
from hashburst_tep.supply_chain import *
class SupplyChainTests(unittest.TestCase):
 def setUp(self):
  self.d=tempfile.TemporaryDirectory();p=Path(self.d.name);self.a=p/"a.tar";self.s=p/"sbom.json";self.pr=p/"prov.json"
  self.a.write_bytes(b"artifact");self.s.write_bytes(b'{"spdxVersion":"SPDX-2.3"}');self.pr.write_bytes(b'{"source":"commit"}')
  self.k=Ed25519PrivateKey.generate();self.raw=self.k.private_bytes(Encoding.Raw,PrivateFormat.Raw,NoEncryption());self.pub=self.k.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw)
  self.m=ReleaseManifest("1.0.0-mainnet","11"*32,"tep.tar",sha256_file(self.a),sha256_file(self.s),sha256_file(self.pr))
 def tearDown(self):self.d.cleanup()
 def test_signed_bundle_verifies(self):self.assertTrue(verify_manifest(self.m,sign_manifest(self.m,self.raw),self.pub,self.a,self.s,self.pr))
 def test_tampered_artifact_rejected(self):
  sig=sign_manifest(self.m,self.raw);self.a.write_bytes(b"tampered");self.assertFalse(verify_manifest(self.m,sig,self.pub,self.a,self.s,self.pr))
 def test_tampered_manifest_rejected(self):
  sig=sign_manifest(self.m,self.raw);x=ReleaseManifest("evil",self.m.source_commit,self.m.artifact_name,self.m.artifact_sha256,self.m.sbom_sha256,self.m.provenance_sha256);self.assertFalse(verify_manifest(x,sig,self.pub,self.a,self.s,self.pr))
 def test_unsigned_or_wrong_key_rejected(self):
  self.assertFalse(verify_manifest(self.m,b"",self.pub,self.a,self.s,self.pr));other=Ed25519PrivateKey.generate().public_key().public_bytes(Encoding.Raw,PublicFormat.Raw);self.assertFalse(verify_manifest(self.m,sign_manifest(self.m,self.raw),other,self.a,self.s,self.pr))
if __name__=="__main__":unittest.main(verbosity=2)
