import unittest
from hashlib import sha3_256
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding,PublicFormat
from hashburst_tep.enrollment import *
from hashburst_tep.governance import *
from hashburst_tep.federation_admission import *
class G7AdmissionTests(unittest.TestCase):
 def setUp(self):
  self.ck=Ed25519PrivateKey.generate();self.cp=self.ck.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw);self.net=sha3_256(b"net").digest();self.gen=sha3_256(b"gen").digest();self.now=1000
  self.keys=[Ed25519PrivateKey.generate() for _ in range(4)];self.pubs=[k.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw) for k in self.keys];self.ids=[sha3_256(b"HB-TEP-NODE-ID-v1\\x00"+p).digest() for p in self.pubs]
  self.gov=GovernanceState(sha3_256(b"fed").digest(),1,tuple(GovernanceMember(i,p,ACTIVE) for i,p in zip(self.ids,self.pubs)))
 def cert(self,i):
  c=EnrollmentCertificate(1,i+1,self.net,self.ids[i],self.pubs[i],"node",900,1100,sha3_256(b"controller").digest(),b"")
  return sign_certificate(c,self.ck)
 def test_four_active_enrolled_admitted(self):
  a=FederationAdmission(self.net,self.gen,self.gov,self.cp,self.now)
  self.assertTrue(all(a.admit(self.ids[i],self.pubs[i],self.cert(i),self.gen) for i in range(4)))
 def test_non_enrolled_rejected(self):
  a=FederationAdmission(self.net,self.gen,self.gov,self.cp,self.now)
  with self.assertRaisesRegex(ValueError,"non-enrolled"):a.admit(self.ids[0],self.pubs[0],None,self.gen)
 def test_foreign_genesis_rejected(self):
  a=FederationAdmission(self.net,self.gen,self.gov,self.cp,self.now)
  with self.assertRaisesRegex(ValueError,"foreign genesis"):a.admit(self.ids[0],self.pubs[0],self.cert(0),bytes(32))
 def test_unauthorized_rejected(self):
  k=Ed25519PrivateKey.generate();p=k.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw);i=sha3_256(b"HB-TEP-NODE-ID-v1\\x00"+p).digest()
  c=EnrollmentCertificate(1,99,self.net,i,p,"node",900,1100,sha3_256(b"controller").digest(),b"");c=sign_certificate(c,self.ck)
  a=FederationAdmission(self.net,self.gen,self.gov,self.cp,self.now)
  with self.assertRaisesRegex(ValueError,"unauthorized"):a.admit(i,p,c,self.gen)
if __name__=="__main__":unittest.main()
