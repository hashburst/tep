import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
from hashburst_tep.cose_sign1 import sign1_ed25519,verify_sign1_ed25519,parse_sign1,CoseError
from hashburst_tep.records_v2 import WindowRecordCore,ledger_record

def pub(k):return k.public_key().public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw)
class CoseRecordTests(unittest.TestCase):
 def setUp(self):
  self.k=Ed25519PrivateKey.generate();self.core=WindowRecordCore(bytes.fromhex("11"*32),bytes.fromhex("22"*32),bytes.fromhex("33"*32),7,bytes.fromhex("44"*32),None,bytes.fromhex("55"*32))
 def test_normative_record_requires_valid_embedded_cose_sign1(self):
  c=sign1_ed25519(self.core.encode(),self.k);r=ledger_record(self.core,c);self.assertEqual(r[2],c);self.assertTrue(verify_sign1_ed25519(c,pub(self.k),self.core.encode()))
 def test_arbitrary_bytes_and_null_rejected_for_normative_record(self):
  with self.assertRaises(ValueError):ledger_record(self.core,b"test-protection")
  with self.assertRaises(ValueError):ledger_record(self.core,None)
 def test_payload_substitution_rejected(self):
  other=self.core.encode()+b"x";c=sign1_ed25519(other,self.k)
  with self.assertRaises(ValueError):ledger_record(self.core,c)
 def test_signature_tamper_fails_verification(self):
  c=bytearray(sign1_ed25519(self.core.encode(),self.k));c[-1]^=1;self.assertFalse(verify_sign1_ed25519(bytes(c),pub(self.k),self.core.encode()))
 def test_wrong_signing_key_fails_verification(self):
  c=sign1_ed25519(self.core.encode(),self.k);other=Ed25519PrivateKey.generate();self.assertFalse(verify_sign1_ed25519(c,pub(other),self.core.encode()))
 def test_legacy_import_is_explicit_and_null_only(self):
  r=ledger_record(self.core,None,legacy_import=True);self.assertIsNone(r[2])
  with self.assertRaises(ValueError):ledger_record(self.core,b"x",legacy_import=True)

if __name__=="__main__":unittest.main(verbosity=2)
