"""Canonical block assembly after successful VDF verification."""
from dataclasses import dataclass
from hashlib import sha3_256
from .domains import POH_OUTPUT_DOMAIN
from .ledger import block_id
from .records import body_root
from .poh.window import VerifiedWindowCandidate

@dataclass(frozen=True)
class AcceptedBlock:
    header:tuple
    records:tuple
    proof:bytes
    block_id:bytes
    h:bytes

def poh_output(challenge,output):
    if not isinstance(challenge,bytes) or len(challenge)!=32:raise ValueError("challenge must be 32 bytes")
    if not isinstance(output,bytes) or not output:raise ValueError("VDF output required")
    return sha3_256(POH_OUTPUT_DOMAIN+challenge+output).digest()

def assemble_verified_block(*,verified,count,previous_h,previous_block_id,vdf_suite,vdf_params_hash,records):
    if not isinstance(verified,VerifiedWindowCandidate):raise ValueError("VerifiedWindowCandidate required")
    if verified.count!=count:raise ValueError("verified count mismatch")
    if not isinstance(verified.result.output,bytes) or not isinstance(verified.result.proof,bytes):raise ValueError("verified VDF result required")
    ids=[];encoded=[]
    for record in records:
        if not isinstance(record,(list,tuple)) or len(record)!=3:raise ValueError("ledger record must be [core, record_id, protection]")
        rid=record[1]
        if not isinstance(rid,bytes) or len(rid)!=32:raise ValueError("record_id must be 32 bytes")
        ids.append(rid);encoded.append(record)
    if tuple(ids)!=tuple(r.record_id for r in verified.records):raise ValueError("records do not match verified registration set and order")
    root=body_root(ids);h=poh_output(verified.challenge,verified.result.output)
    header=[1,count,previous_h,previous_block_id,h,vdf_suite,vdf_params_hash,root]
    bid=block_id(header,encoded)
    return AcceptedBlock(tuple(header),tuple(encoded),verified.result.proof,bid,h)
