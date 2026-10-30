"""Canonical TEP peer identity and v2.2 compatibility binding."""
from dataclasses import dataclass
from hashlib import sha3_256
from .encoding import dumps

IDENTITY_DOMAIN=b"HB-TEP-IDENTITY-v1\x00"
ADDRESS_DOMAIN=b"HB-TEP-ADDRESS-v1\x00"

def _b32(n,v):
    if not isinstance(v,bytes) or len(v)!=32:raise ValueError(f"{n} must be 32 bytes")
def _text(n,v,max_len):
    if not isinstance(v,str):raise ValueError(f"{n} must be string")
    v=v.strip()
    if not v or len(v)>max_len:raise ValueError(f"{n} must be non-empty and at most {max_len} characters")
    return v

@dataclass(frozen=True)
class PeerIdentity:
    signing_public_key:bytes
    transport_public_key:bytes
    def values(self):
        _b32("signing_public_key",self.signing_public_key);_b32("transport_public_key",self.transport_public_key)
        return [1,self.signing_public_key,self.transport_public_key]
    def identity_id(self):return sha3_256(IDENTITY_DOMAIN+dumps(self.values())).digest()
    def ledger_address(self,network_id):
        _b32("network_id",network_id)
        return sha3_256(ADDRESS_DOMAIN+network_id+self.identity_id()).digest()

@dataclass(frozen=True)
class LegacyBinding:
    identity_id:bytes
    node_id:str
    peer_id:str
    x25519_public_key:bytes
    def values(self):
        _b32("identity_id",self.identity_id);_b32("x25519_public_key",self.x25519_public_key)
        return [1,self.identity_id,_text("node_id",self.node_id,128),_text("peer_id",self.peer_id,256),self.x25519_public_key]
    def wire_node_field(self):
        return self.node_id.encode("ascii","replace")[:16].ljust(16,b"\x00")
    def validate_for(self,identity):
        return self.identity_id==identity.identity_id() and self.x25519_public_key==identity.transport_public_key
