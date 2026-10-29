"""Deterministic TEP genesis construction."""
from dataclasses import dataclass
from hashlib import sha3_256
from .domains import GENESIS_DOMAIN
from .encoding import dumps

def _b32(name,value):
    if not isinstance(value,bytes) or len(value)!=32: raise ValueError(f"{name} must be 32 bytes")
    return value

@dataclass(frozen=True)
class Genesis:
    network_id: bytes
    protocol_version: int
    vdf_suite: int
    vdf_params_hash: bytes
    def descriptor(self):
        _b32("network_id",self.network_id); _b32("vdf_params_hash",self.vdf_params_hash)
        return [1,self.network_id,self.protocol_version,self.vdf_suite,self.vdf_params_hash]
    def encode(self): return dumps(self.descriptor())
    def h0(self): return sha3_256(GENESIS_DOMAIN+self.encode()).digest()
