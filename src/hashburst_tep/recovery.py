"""Finalized-ledger checkpoint persistence and recovery helpers."""
from dataclasses import dataclass
from pathlib import Path
from .checkpoint import Checkpoint,atomic_write,decode_checkpoint

@dataclass(frozen=True)
class FinalizedState:
    checkpoint:Checkpoint
    checkpoint_id:bytes

def persist_finalized(path,checkpoint):
    payload=checkpoint.checkpoint_id()+checkpoint.encode()
    atomic_write(path,payload)
    return FinalizedState(checkpoint,checkpoint.checkpoint_id())

def load_finalized(path,decoder=decode_checkpoint):
    data=Path(path).read_bytes()
    if len(data)<33:raise ValueError("checkpoint file truncated")
    expected,payload=data[:32],data[32:]
    cp=decoder(payload)
    if cp.checkpoint_id()!=expected:raise ValueError("checkpoint integrity failure")
    return FinalizedState(cp,expected)
