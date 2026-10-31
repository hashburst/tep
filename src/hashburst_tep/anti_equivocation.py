"""Persistent anti-equivocation vote locks for production governance/finality."""
from dataclasses import dataclass
from hashlib import sha3_256
import json,os,tempfile
from .encoding import dumps
from .domains import ANTI_EQUIVOCATION_LOCK_DOMAIN

def _b32(n,v):
    if not isinstance(v,bytes) or len(v)!=32:raise ValueError(f"{n} must be 32 bytes")
def _u64(n,v):
    if not isinstance(v,int) or isinstance(v,bool) or not 0<=v<2**64:raise ValueError(f"{n} must be uint64")

@dataclass(frozen=True)
class VoteLockKey:
    federation_id:bytes
    validator_set_version:int
    count:int
    validator_id:bytes
    def values(self):
        _b32("federation_id",self.federation_id);_u64("validator_set_version",self.validator_set_version);_u64("count",self.count);_b32("validator_id",self.validator_id)
        return [1,self.federation_id,self.validator_set_version,self.count,self.validator_id]
    def digest(self):return sha3_256(ANTI_EQUIVOCATION_LOCK_DOMAIN+dumps(self.values())).digest()

class PersistentVoteLock:
    def __init__(self,path):
        self.path=os.fspath(path);self._locks={}
        if os.path.exists(self.path):
            raw=json.load(open(self.path,"r",encoding="utf-8"))
            if raw.get("schema")!="hb-vote-lock-v1":raise ValueError("unsupported vote-lock schema")
            self._locks=dict(raw.get("locks",{}))
    def _save(self):
        directory=os.path.dirname(self.path) or ".";os.makedirs(directory,exist_ok=True)
        obj={"schema":"hb-vote-lock-v1","locks":dict(sorted(self._locks.items()))}
        fd,tmp=tempfile.mkstemp(prefix=".vote-lock-",dir=directory,text=True)
        try:
            with os.fdopen(fd,"w",encoding="utf-8") as h:json.dump(obj,h,sort_keys=True,separators=(",",":"));h.flush();os.fsync(h.fileno())
            os.replace(tmp,self.path);dfd=os.open(directory,os.O_RDONLY)
            try:os.fsync(dfd)
            finally:os.close(dfd)
        finally:
            if os.path.exists(tmp):os.unlink(tmp)
    def authorize(self,key,proposal_digest):
        _b32("proposal_digest",proposal_digest);kh=key.digest().hex();ph=proposal_digest.hex();prior=self._locks.get(kh)
        if prior is None:
            self._locks[kh]=ph;self._save();return "LOCKED"
        if prior==ph:return "IDEMPOTENT"
        raise ValueError("equivocation rejected")
    def locked_digest(self,key):
        v=self._locks.get(key.digest().hex());return None if v is None else bytes.fromhex(v)
