"""Canonical window-bound record schema for the normative CG-WESO RC1 profile."""
from dataclasses import dataclass
from hashlib import sha3_256
from .domains import RECORD_DOMAIN
from .encoding import dumps
from .cose_sign1 import parse_sign1

def _b32(name,value):
    if not isinstance(value,bytes) or len(value)!=32:raise ValueError(f"{name} must be 32 bytes")
def _u64(name,value):
    if not isinstance(value,int) or isinstance(value,bool) or not 0<=value<2**64:raise ValueError(f"{name} must be uint64")

@dataclass(frozen=True)
class WindowRecordCore:
    sender_id:bytes;recipient_id:bytes;packet_id:bytes;sequence:int;prior_block_id:bytes;certified_time:int|None;payload_digest:bytes
    def values(self):
        for n,v in (("sender_id",self.sender_id),("recipient_id",self.recipient_id),("packet_id",self.packet_id),("prior_block_id",self.prior_block_id),("payload_digest",self.payload_digest)):_b32(n,v)
        _u64("sequence",self.sequence)
        if self.certified_time is not None:_u64("certified_time",self.certified_time)
        return [2,self.sender_id,self.recipient_id,self.packet_id,self.sequence,self.prior_block_id,self.certified_time,self.payload_digest]
    def encode(self):return dumps(self.values())
    def record_id(self):return sha3_256(RECORD_DOMAIN+self.encode()).digest()

def ledger_record(core,protection,legacy_import=False):
    rid=core.record_id()
    if legacy_import:
        if protection is not None:raise ValueError("legacy/import protection must be null")
        return [core.values(),rid,None]
    if not isinstance(protection,bytes):raise ValueError("normative RC1 record requires encoded COSE_Sign1")
    try:_,payload,_=parse_sign1(protection)
    except Exception as exc:raise ValueError("invalid normative COSE_Sign1 protection") from exc
    if payload!=core.encode():raise ValueError("COSE_Sign1 payload must equal canonical record core")
    return [core.values(),rid,protection]
