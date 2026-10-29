"""Signed TEP identity binding and continuity-controlled rotation."""
from dataclasses import dataclass
from hashlib import sha3_256
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from .encoding import dumps
from .identity import PeerIdentity,LegacyBinding

BINDING_DOMAIN=b"HB-TEP-IDENTITY-BINDING-v1\x00"
ROTATION_DOMAIN=b"HB-TEP-IDENTITY-ROTATION-v1\x00"

def _u64(name,v):
    if not isinstance(v,int) or isinstance(v,bool) or not 0<=v<2**64:raise ValueError(f"{name} must be uint64")
def _b32(name,v):
    if not isinstance(v,bytes) or len(v)!=32:raise ValueError(f"{name} must be 32 bytes")

@dataclass(frozen=True)
class BindingStatement:
    network_id:bytes
    sequence:int
    identity:PeerIdentity
    legacy:LegacyBinding
    def values(self):
        _b32("network_id",self.network_id);_u64("sequence",self.sequence)
        if not self.legacy.validate_for(self.identity):raise ValueError("legacy binding does not match identity")
        return [1,self.network_id,self.sequence,self.identity.values(),self.legacy.values()]
    def message(self):return BINDING_DOMAIN+dumps(self.values())
    def digest(self):return sha3_256(self.message()).digest()

@dataclass(frozen=True)
class SignedBinding:
    statement:BindingStatement
    signature:bytes

def verify_signed_binding(signed):
    try:
        Ed25519PublicKey.from_public_bytes(signed.statement.identity.signing_public_key).verify(signed.signature,signed.statement.message())
        return True
    except Exception:return False

@dataclass(frozen=True)
class RotationStatement:
    network_id:bytes
    sequence:int
    previous_identity_id:bytes
    next_binding_digest:bytes
    def values(self):
        _b32("network_id",self.network_id);_u64("sequence",self.sequence)
        _b32("previous_identity_id",self.previous_identity_id);_b32("next_binding_digest",self.next_binding_digest)
        return [1,self.network_id,self.sequence,self.previous_identity_id,self.next_binding_digest]
    def message(self):return ROTATION_DOMAIN+dumps(self.values())

@dataclass(frozen=True)
class AuthorizedRotation:
    next_binding:SignedBinding
    continuity:RotationStatement
    previous_signature:bytes

def verify_rotation(rotation,previous_identity,previous_sequence):
    try:
        nb=rotation.next_binding;rs=rotation.continuity
        if not verify_signed_binding(nb):return False
        if rs.network_id!=nb.statement.network_id:return False
        if rs.previous_identity_id!=previous_identity.identity_id():return False
        if rs.next_binding_digest!=nb.statement.digest():return False
        if rs.sequence!=nb.statement.sequence:return False
        if rs.sequence!=previous_sequence+1:return False
        if nb.statement.identity.identity_id()==previous_identity.identity_id():return False
        Ed25519PublicKey.from_public_bytes(previous_identity.signing_public_key).verify(rotation.previous_signature,rs.message())
        return True
    except Exception:return False
