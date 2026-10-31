"""Immutable production genesis and network configuration binding."""
from dataclasses import dataclass
from hashlib import sha3_256
import json,os,tempfile
from .encoding import dumps
from .domains import NETWORK_GENESIS_DOMAIN,NETWORK_CONFIG_DOMAIN
from .federation import ValidatorSet

def _b32(n,v):
    if not isinstance(v,bytes) or len(v)!=32:raise ValueError(f"{n} must be 32 bytes")
def _u64(n,v):
    if not isinstance(v,int) or isinstance(v,bool) or not 0<=v<2**64:raise ValueError(f"{n} must be uint64")

@dataclass(frozen=True)
class ConsensusParameters:
    finality_threshold_numerator:int
    finality_threshold_denominator:int
    max_clock_skew_seconds:int
    def values(self):
        for n,v in (("finality_threshold_numerator",self.finality_threshold_numerator),("finality_threshold_denominator",self.finality_threshold_denominator),("max_clock_skew_seconds",self.max_clock_skew_seconds)):_u64(n,v)
        if self.finality_threshold_denominator==0 or self.finality_threshold_numerator>self.finality_threshold_denominator:raise ValueError("invalid finality threshold")
        return [1,self.finality_threshold_numerator,self.finality_threshold_denominator,self.max_clock_skew_seconds]

@dataclass(frozen=True)
class VDFParameters:
    suite:bytes
    discriminant_bits:int
    iterations:int
    def values(self):
        if not isinstance(self.suite,bytes) or not self.suite or len(self.suite)>64:raise ValueError("invalid VDF suite")
        _u64("discriminant_bits",self.discriminant_bits);_u64("iterations",self.iterations)
        if self.discriminant_bits<512 or self.iterations==0:raise ValueError("unsafe VDF parameters")
        return [1,self.suite,self.discriminant_bits,self.iterations]
    def digest(self):return sha3_256(NETWORK_CONFIG_DOMAIN+dumps(self.values())).digest()

@dataclass(frozen=True)
class ProductionGenesis:
    network_id:bytes
    chain_id:bytes
    protocol_version:int
    initial_validator_set:ValidatorSet
    consensus:ConsensusParameters
    vdf:VDFParameters
    def values(self):
        _b32("network_id",self.network_id);_b32("chain_id",self.chain_id);_u64("protocol_version",self.protocol_version)
        return [1,self.network_id,self.chain_id,self.protocol_version,self.initial_validator_set.version,self.initial_validator_set.digest(),self.consensus.values(),self.vdf.values()]
    def encode(self):return dumps(self.values())
    def genesis_id(self):return sha3_256(NETWORK_GENESIS_DOMAIN+self.encode()).digest()

class PersistentGenesisRegistry:
    def __init__(self,path):
        self.path=os.fspath(path);self.record=None
        if os.path.exists(self.path):
            raw=json.load(open(self.path,"r",encoding="utf-8"))
            if raw.get("schema")!="hb-production-genesis-v1":raise ValueError("unsupported genesis registry schema")
            self.record=raw
    def bind(self,genesis):
        gid=genesis.genesis_id().hex();enc=genesis.encode().hex()
        candidate={"schema":"hb-production-genesis-v1","network_id":genesis.network_id.hex(),"chain_id":genesis.chain_id.hex(),"genesis_id":gid,"canonical_genesis":enc}
        if self.record is not None:
            if self.record!=candidate:raise ValueError("genesis mutation or cross-network configuration rejected")
            return "IDEMPOTENT"
        directory=os.path.dirname(self.path) or ".";os.makedirs(directory,exist_ok=True);fd,tmp=tempfile.mkstemp(prefix=".genesis-",dir=directory,text=True)
        try:
            with os.fdopen(fd,"w",encoding="utf-8") as h:json.dump(candidate,h,sort_keys=True,separators=(",",":"));h.flush();os.fsync(h.fileno())
            os.replace(tmp,self.path);dfd=os.open(directory,os.O_RDONLY)
            try:os.fsync(dfd)
            finally:os.close(dfd)
        finally:
            if os.path.exists(tmp):os.unlink(tmp)
        self.record=candidate;return "BOUND"
    def require(self,network_id,chain_id,genesis_id):
        if self.record is None:raise ValueError("genesis not bound")
        for n,v in (("network_id",network_id),("chain_id",chain_id),("genesis_id",genesis_id)):_b32(n,v)
        if self.record["network_id"]!=network_id.hex() or self.record["chain_id"]!=chain_id.hex() or self.record["genesis_id"]!=genesis_id.hex():raise ValueError("foreign network/genesis rejected")
        return True
