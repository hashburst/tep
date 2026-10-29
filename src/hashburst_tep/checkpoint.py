"""Finalized checkpoint construction and atomic persistence."""
import os,tempfile
from dataclasses import dataclass
from hashlib import sha3_256
from pathlib import Path
from .domains import CHECKPOINT_DOMAIN
from .encoding import dumps

def _b32(name,value):
    if not isinstance(value,bytes) or len(value)!=32: raise ValueError(f"{name} must be 32 bytes")

def _u64(name,value):
    if not isinstance(value,int) or isinstance(value,bool) or not 0<=value<2**64: raise ValueError(f"{name} must be uint64")

@dataclass(frozen=True)
class Checkpoint:
    network_id: bytes; count: int; h: bytes; block_id: bytes; vdf_params_hash: bytes
    validator_set_version: int; quorum_certificate_digest: bytes
    def values(self):
        for n,v in (("network_id",self.network_id),("h",self.h),("block_id",self.block_id),("vdf_params_hash",self.vdf_params_hash),("quorum_certificate_digest",self.quorum_certificate_digest)):_b32(n,v)
        _u64("count",self.count);_u64("validator_set_version",self.validator_set_version)
        return [1,self.network_id,self.count,self.h,self.block_id,self.vdf_params_hash,self.validator_set_version,self.quorum_certificate_digest]
    def encode(self): return dumps(self.values())
    def checkpoint_id(self): return sha3_256(CHECKPOINT_DOMAIN+self.encode()).digest()

def atomic_write(path,data):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(prefix=path.name+".",dir=path.parent)
    try:
        with os.fdopen(fd,"wb") as f:f.write(data);f.flush();os.fsync(f.fileno())
        if Path(tmp).read_bytes()!=data:raise IOError("checkpoint read-back mismatch")
        os.replace(tmp,path)
        dfd=os.open(path.parent,os.O_RDONLY)
        try:os.fsync(dfd)
        finally:os.close(dfd)
    except Exception:
        try:os.unlink(tmp)
        except FileNotFoundError:pass
        raise
