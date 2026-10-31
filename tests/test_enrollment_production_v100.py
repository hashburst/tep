import unittest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from hashburst_tep.enrollment import *

class EnrollmentProductionTests(unittest.TestCase):
    def setUp(self):
        self.controller=Ed25519PrivateKey.generate()
        self.node=Ed25519PrivateKey.generate()
        self.network=b"N"*32;self.node_id=b"I"*32;self.controller_id=b"C"*32
    def cert(self,scope="node",serial=1,nb=100,na=200):
        from cryptography.hazmat.primitives.serialization import Encoding,PublicFormat
        pk=self.node.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw)
        c=EnrollmentCertificate(1,serial,self.network,self.node_id,pk,scope,nb,na,self.controller_id)
        return sign_certificate(c,self.controller)
    def test_signed_certificate_valid(self):
        c=self.cert();self.assertTrue(verify_certificate(c,self.controller.public_key(),150,self.network))
    def test_expired_and_wrong_network_rejected(self):
        c=self.cert();self.assertFalse(verify_certificate(c,self.controller.public_key(),200,self.network));self.assertFalse(verify_certificate(c,self.controller.public_key(),150,b"X"*32))
    def test_tamper_and_wrong_controller_rejected(self):
        c=self.cert();bad=EnrollmentCertificate(**{**c.__dict__,"node_id":b"Z"*32})
        self.assertFalse(verify_certificate(bad,self.controller.public_key(),150,self.network))
        self.assertFalse(verify_certificate(c,Ed25519PrivateKey.generate().public_key(),150,self.network))
    def test_validator_scope_cannot_be_enrolled(self):
        with self.assertRaises(ValueError):self.cert(scope="validator")
    def test_challenge_replay_rejected(self):
        r=EnrollmentRegistry();q=b"Q"*32;r.consume_challenge(q)
        with self.assertRaises(ValueError):r.consume_challenge(q)
    def test_duplicate_serial_and_revocation(self):
        r=EnrollmentRegistry();c=self.cert();cid=r.register(c)
        with self.assertRaises(ValueError):r.register(self.cert())
        self.assertFalse(r.is_revoked(cid));r.revoke(cid);self.assertTrue(r.is_revoked(cid))
    def test_node_challenge_signature(self):
        q=b"Q"*32;m=challenge_message(self.network,self.node_id,q);sig=self.node.sign(m)
        self.node.public_key().verify(sig,m)
        with self.assertRaises(Exception):self.node.public_key().verify(sig,challenge_message(self.network,self.node_id,b"R"*32))

if __name__=="__main__":unittest.main()
