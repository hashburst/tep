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


class PersistentEnrollmentRegistry:
    """Crash-safe JSON registry for consumed challenges, certificates and revocations."""
    def __init__(self,path):
        import json,os
        self.path=os.fspath(path);self._json=json
        self._state={"next_serial":1,"used_challenges":[],"certificates":{},"revoked":[]}
        if os.path.exists(self.path):
            with open(self.path,"r",encoding="utf-8") as h:self._state=json.load(h)
    def _save(self):
        import os,tempfile
        directory=os.path.dirname(self.path) or ".";os.makedirs(directory,exist_ok=True)
        fd,tmp=tempfile.mkstemp(prefix=".enrollment-",dir=directory,text=True)
        try:
            with os.fdopen(fd,"w",encoding="utf-8") as h:
                self._json.dump(self._state,h,sort_keys=True,separators=(",",":"));h.flush();os.fsync(h.fileno())
            os.replace(tmp,self.path)
            dfd=os.open(directory,os.O_RDONLY)
            try:os.fsync(dfd)
            finally:os.close(dfd)
        finally:
            if os.path.exists(tmp):os.unlink(tmp)
    def consume_challenge(self,challenge):
        _b32("challenge",challenge);hx=challenge.hex()
        if hx in self._state["used_challenges"]:raise ValueError("challenge replay")
        self._state["used_challenges"].append(hx);self._save()
    def allocate_serial(self):
        serial=self._state["next_serial"];_u64("serial",serial)
        self._state["next_serial"]=serial+1;self._save();return serial
    def register(self,cert):
        key=str(cert.serial)
        if key in self._state["certificates"]:raise ValueError("duplicate enrollment serial")
        cid=cert.certificate_id();self._state["certificates"][key]=cid.hex();self._save();return cid
    def revoke(self,certificate_id):
        _b32("certificate_id",certificate_id);hx=certificate_id.hex()
        if hx not in self._state["revoked"]:self._state["revoked"].append(hx);self._save()
    def is_revoked(self,certificate_id):return certificate_id.hex() in self._state["revoked"]

class EnrollmentController:
    """Persistent controller identity and certificate issuer; never grants validator scope."""
    def __init__(self,state_dir,network_id):
        import os
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        from cryptography.hazmat.primitives.serialization import Encoding,PrivateFormat,PublicFormat,NoEncryption
        _b32("network_id",network_id);self.network_id=network_id;os.makedirs(state_dir,exist_ok=True)
        self._key_path=os.path.join(state_dir,"enrollment-controller-ed25519.key")
        if os.path.exists(self._key_path):
            raw=open(self._key_path,"rb").read()
            if len(raw)!=32:raise ValueError("invalid controller private key")
            self.private_key=Ed25519PrivateKey.from_private_bytes(raw)
        else:
            self.private_key=Ed25519PrivateKey.generate()
            raw=self.private_key.private_bytes(Encoding.Raw,PrivateFormat.Raw,NoEncryption())
            fd=os.open(self._key_path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
            with os.fdopen(fd,"wb") as h:h.write(raw);h.flush();os.fsync(h.fileno())
        self.public_key_bytes=self.private_key.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw)
        self.controller_id=sha3_256(b"HB-TEP-ENROLLMENT-CONTROLLER-v1\\x00"+self.public_key_bytes).digest()
        self.registry=PersistentEnrollmentRegistry(os.path.join(state_dir,"enrollment-registry.json"))
    def issue(self,node_id,node_public_key,scope,not_before,not_after,challenge,challenge_signature):
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        _b32("node_id",node_id);_b32("node_public_key",node_public_key);_b32("challenge",challenge)
        Ed25519PublicKey.from_public_bytes(node_public_key).verify(challenge_signature,challenge_message(self.network_id,node_id,challenge))
        self.registry.consume_challenge(challenge)
        serial=self.registry.allocate_serial()
        cert=EnrollmentCertificate(1,serial,self.network_id,node_id,node_public_key,scope,not_before,not_after,self.controller_id)
        cert=sign_certificate(cert,self.private_key);self.registry.register(cert);return cert
