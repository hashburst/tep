"""Deterministic ledger primitives. No VDF implementation is imported here."""
from hashlib import sha3_256
from .domains import POH_INPUT_DOMAIN,BLOCK_DOMAIN
from .encoding import dumps,uint64be

def _b32(name,value):
    if not isinstance(value,bytes) or len(value)!=32: raise ValueError(f"{name} must be 32 bytes")
    return value

def next_count(previous):
    if not isinstance(previous,int) or isinstance(previous,bool) or not 0<=previous<2**64-1: raise ValueError("previous count cannot advance")
    return previous+1

def poh_input(network_id,count,previous_h,previous_block_id,vdf_params_hash):
    for n,v in (("network_id",network_id),("previous_h",previous_h),("previous_block_id",previous_block_id),("vdf_params_hash",vdf_params_hash)):_b32(n,v)
    return sha3_256(POH_INPUT_DOMAIN+network_id+uint64be(count)+previous_h+previous_block_id+vdf_params_hash).digest()

def block_id(header,records):
    return sha3_256(BLOCK_DOMAIN+dumps([header,list(records)])).digest()
