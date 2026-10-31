"""Production enrollment primitives for HashBurst TEP v1.0.

Enrollment proves node identity and authorization scope.  It deliberately cannot
grant validator membership; validator admission belongs to the governance gate.
"""
from dataclasses import dataclass
from hashlib import sha3_256
from .encoding import dumps

ENROLLMENT_CERT_DOMAIN=b"HB-TEP-ENROLLMENT-CERT-v1\x00"
ENROLLMENT_CHALLENGE_DOMAIN=b"HB-TEP-ENROLLMENT-CHALLENGE-v1\x00"
ALLOWED_SCOPES=frozenset({"node","observer","storage","mining-worker","mining-orchestrator"})
FORBIDDEN_SCOPES=frozenset({"validator","governance","controller"})

def _b32(name,value):
    if not isinstance(value,bytes) or len(value)!=32: raise ValueError(f"{name} must be 32 bytes")
def _u64(name,value):
    if not isinstance(value,int) or isinstance(value,bool) or not 0<=value<2**64: raise ValueError(f"{name} must be uint64")

@dataclass(frozen=True)
class EnrollmentCertificate:
    version:int
    serial:int
    network_id:bytes
    node_id:bytes
    node_public_key:bytes
    scope:str
    not_before:int
    not_after:int
    controller_id:bytes
    signature:bytes=b""

    def unsigned_values(self):
        if self.version!=1: raise ValueError("unsupported enrollment certificate version")
        _u64("serial",self.serial); _u64("not_before",self.not_before); _u64("not_after",self.not_after)
        for n,v in (("network_id",self.network_id),("node_id",self.node_id),("node_public_key",self.node_public_key),("controller_id",self.controller_id)):_b32(n,v)
        if self.not_after<=self.not_before: raise ValueError("invalid certificate validity interval")
        if self.scope in FORBIDDEN_SCOPES or self.scope not in ALLOWED_SCOPES: raise ValueError("scope is not enrollment-authorizable")
        return [1,self.serial,self.network_id,self.node_id,self.node_public_key,self.scope.encode("ascii"),self.not_before,self.not_after,self.controller_id]

    def message(self): return ENROLLMENT_CERT_DOMAIN+dumps(self.unsigned_values())
    def certificate_id(self): return sha3_256(self.message()+self.signature).digest()

def sign_certificate(cert,controller_private_key):
    sig=controller_private_key.sign(cert.message())
    return EnrollmentCertificate(**{**cert.__dict__,"signature":sig})

def verify_certificate(cert,controller_public_key,now,expected_network_id=None):
    try:
        if expected_network_id is not None and cert.network_id!=expected_network_id:return False
        _u64("now",now)
        if not cert.not_before<=now<cert.not_after:return False
        if len(cert.signature)!=64:return False
        controller_public_key.verify(cert.signature,cert.message())
        return True
    except Exception:return False

def challenge_message(network_id,node_id,challenge):
    _b32("network_id",network_id);_b32("node_id",node_id);_b32("challenge",challenge)
    return ENROLLMENT_CHALLENGE_DOMAIN+dumps([1,network_id,node_id,challenge])

class EnrollmentRegistry:
    """In-memory policy core; persistence adapters must preserve these invariants."""
    def __init__(self):
        self._used_challenges=set();self._certs={};self._revoked=set()
    def consume_challenge(self,challenge):
        _b32("challenge",challenge)
        if challenge in self._used_challenges:raise ValueError("challenge replay")
        self._used_challenges.add(challenge)
    def register(self,cert):
        cid=cert.certificate_id()
        if cert.serial in self._certs:raise ValueError("duplicate enrollment serial")
        self._certs[cert.serial]=cid
        return cid
    def revoke(self,certificate_id):
        _b32("certificate_id",certificate_id);self._revoked.add(certificate_id)
    def is_revoked(self,certificate_id):return certificate_id in self._revoked
