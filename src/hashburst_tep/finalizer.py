"""Finality gate: persist a checkpoint only after QC verification."""
from .checkpoint import Checkpoint
from .federation import verify_qc
from .recovery import persist_finalized

def finalize_verified_block(path,*,network_id,block,vdf_params_hash,validator_set,qc):
    if qc.network_id!=network_id or qc.count!=block.header[1] or qc.block_id!=block.block_id:raise ValueError("QC does not identify block")
    if not verify_qc(qc,validator_set):raise ValueError("invalid or insufficient quorum certificate")
    cp=Checkpoint(network_id,block.header[1],block.h,block.block_id,vdf_params_hash,validator_set.version,qc.digest())
    return persist_finalized(path,cp)
