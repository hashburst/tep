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

    def test_persistent_controller_restart_replay_and_serial(self):
        import tempfile
        from cryptography.hazmat.primitives.serialization import Encoding,PublicFormat
        with tempfile.TemporaryDirectory() as d:
            c1=EnrollmentController(d,self.network);pk=self.node.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw)
            q=b"A"*32;sig=self.node.sign(challenge_message(self.network,self.node_id,q))
            cert1=c1.issue(self.node_id,pk,"node",100,200,q,sig);controller_id=c1.controller_id
            c2=EnrollmentController(d,self.network);self.assertEqual(c2.controller_id,controller_id)
            self.assertTrue(verify_certificate(cert1,c2.private_key.public_key(),150,self.network))
            with self.assertRaises(ValueError):c2.issue(self.node_id,pk,"node",100,200,q,sig)
            q2=b"B"*32;sig2=self.node.sign(challenge_message(self.network,self.node_id,q2))
            cert2=c2.issue(self.node_id,pk,"storage",100,200,q2,sig2)
            self.assertGreater(cert2.serial,cert1.serial)
            c2.registry.revoke(cert1.certificate_id())
            c3=EnrollmentController(d,self.network);self.assertTrue(c3.registry.is_revoked(cert1.certificate_id()))
    def test_controller_rejects_invalid_node_signature_and_validator_scope(self):
        import tempfile
        from cryptography.hazmat.primitives.serialization import Encoding,PublicFormat
        with tempfile.TemporaryDirectory() as d:
            c=EnrollmentController(d,self.network);pk=self.node.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw);q=b"D"*32
            with self.assertRaises(Exception):c.issue(self.node_id,pk,"node",100,200,q,b"0"*64)
            sig=self.node.sign(challenge_message(self.network,self.node_id,q))
            with self.assertRaises(ValueError):c.issue(self.node_id,pk,"validator",100,200,q,sig)
if __name__=="__main__":unittest.main()
