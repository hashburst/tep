"""End-to-end RC1 ledger orchestration without custody of validator private keys."""
from dataclasses import dataclass
from .ledger import next_count,poh_input
from .poh import EvaluationWindow
from .block import assemble_verified_block
from .federation import QuorumCertificate
from .finalizer import finalize_verified_block

@dataclass(frozen=True)
class PreviousLedgerState:
    count:int
    h:bytes
    block_id:bytes

@dataclass(frozen=True)
class PreparedBlock:
    block:object
    vote_message:bytes
    validator_set_digest:bytes

class LedgerOrchestrator:
    def __init__(self,*,network_id,vdf_params_hash,vdf_suite,iterations,adapter,validator_set):
        self.network_id=network_id;self.vdf_params_hash=vdf_params_hash;self.vdf_suite=vdf_suite
        self.iterations=iterations;self.adapter=adapter;self.validator_set=validator_set
    def prepare(self,previous,records):
        count=next_count(previous.count)
        challenge=poh_input(self.network_id,count,previous.h,previous.block_id,self.vdf_params_hash)
        w=EvaluationWindow(self.adapter);w.start(challenge,count,self.iterations)
        by_id={}
        for record in records:
            if not isinstance(record,(list,tuple)) or len(record)!=3:raise ValueError("ledger record required")
            rid=record[1]
            if rid in by_id:raise ValueError("duplicate record_id")
            core=record[0];certified_time=core[6] if isinstance(core,(list,tuple)) and len(core)==8 and core[0]==2 else None
            w.register(rid,certified_time);by_id[rid]=record
        candidate=w.evaluate_and_close()
        verified=w.verify(candidate)
        if verified is None:raise ValueError("VDF verification failed")
        ordered=tuple(by_id[r.record_id] for r in verified.records)
        block=assemble_verified_block(verified=verified,count=count,previous_h=previous.h,previous_block_id=previous.block_id,vdf_suite=self.vdf_suite,vdf_params_hash=self.vdf_params_hash,records=ordered)
        shell=QuorumCertificate(self.validator_set.version,self.validator_set.digest(),self.network_id,count,block.block_id,())
        return PreparedBlock(block,shell.message(),self.validator_set.digest())
    def make_qc(self,prepared,votes):
        return QuorumCertificate(self.validator_set.version,prepared.validator_set_digest,self.network_id,prepared.block.header[1],prepared.block.block_id,tuple(votes))
    def finalize(self,path,prepared,votes):
        qc=self.make_qc(prepared,votes)
        return finalize_verified_block(path,network_id=self.network_id,block=prepared.block,vdf_params_hash=self.vdf_params_hash,validator_set=self.validator_set,qc=qc)
