"""Versioned Ed25519 federation finality for TEP v0.2.0-rc1."""
from dataclasses import dataclass
from hashlib import sha3_256
from .domains import FINALITY_VOTE_DOMAIN,FINALITY_QC_DOMAIN,VALIDATOR_SET_DOMAIN
from .encoding import dumps

def _b32(n,v):
    if not isinstance(v,bytes) or len(v)!=32:raise ValueError(f"{n} must be 32 bytes")
def _u64(n,v):
    if not isinstance(v,int) or isinstance(v,bool) or not 0<=v<2**64:raise ValueError(f"{n} must be uint64")

@dataclass(frozen=True)
class Validator:
    validator_id:bytes
    public_key:bytes
    def values(self):
        _b32("validator_id",self.validator_id);_b32("public_key",self.public_key);return [self.validator_id,self.public_key]

@dataclass(frozen=True)
class ValidatorSet:
    version:int
    validators:tuple
    def ordered(self):
        _u64("validator_set_version",self.version)
        vals=tuple(sorted(self.validators,key=lambda x:x.validator_id))
        if not vals:raise ValueError("validator set must not be empty")
        ids=[v.validator_id for v in vals]
        if len(ids)!=len(set(ids)):raise ValueError("duplicate validator_id")
        keys=[v.public_key for v in vals]
        if len(keys)!=len(set(keys)):raise ValueError("duplicate validator public key")
        for v in vals:v.values()
        return vals
    def digest(self):return sha3_256(VALIDATOR_SET_DOMAIN+dumps([1,self.version,[v.values() for v in self.ordered()]])).digest()
    def threshold(self):return (2*len(self.ordered()))//3+1

@dataclass(frozen=True)
class FinalityVote:
    validator_id:bytes
    signature:bytes

@dataclass(frozen=True)
class QuorumCertificate:
    validator_set_version:int
    validator_set_digest:bytes
    network_id:bytes
    count:int
    block_id:bytes
    votes:tuple
    def message(self):
        for n,v in (("validator_set_digest",self.validator_set_digest),("network_id",self.network_id),("block_id",self.block_id)):_b32(n,v)
        _u64("validator_set_version",self.validator_set_version);_u64("count",self.count)
        return FINALITY_VOTE_DOMAIN+dumps([1,self.validator_set_version,self.validator_set_digest,self.network_id,self.count,self.block_id])
    def digest(self):
        ordered=sorted(self.votes,key=lambda v:v.validator_id)
        return sha3_256(FINALITY_QC_DOMAIN+dumps([1,self.validator_set_version,self.validator_set_digest,self.network_id,self.count,self.block_id,[[v.validator_id,v.signature] for v in ordered]])).digest()

def verify_qc(qc,validator_set):
    if qc.validator_set_version!=validator_set.version or qc.validator_set_digest!=validator_set.digest():return False
    try:message=qc.message();members={v.validator_id:v.public_key for v in validator_set.ordered()}
    except ValueError:return False
    seen=set();valid=0
    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        for vote in qc.votes:
            _b32("validator_id",vote.validator_id)
            if vote.validator_id in seen or vote.validator_id not in members:return False
            seen.add(vote.validator_id)
            Ed25519PublicKey.from_public_bytes(members[vote.validator_id]).verify(vote.signature,message)
            valid+=1
    except Exception:return False
    return valid>=validator_set.threshold()
