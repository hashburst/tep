"""Data model for the pre-finality PoH state machine."""
from dataclasses import dataclass
from enum import Enum
from ..vdf.adapter import VDFResult

class PoHPhase(Enum):
    IDLE="idle";EVALUATING="evaluating";CLOSED="closed";VERIFIED="verified"

@dataclass(frozen=True)
class BoundRecord:
    record_id: bytes
    iteration_index: int
    iteration_state_digest: bytes
    certified_time: int|None=None

@dataclass(frozen=True)
class PoHCandidate:
    count: int
    challenge: bytes
    result: VDFResult
    records: tuple[BoundRecord,...]
