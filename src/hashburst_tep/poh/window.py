"""Registration-window binding for VDF adapters without progress observation."""
from dataclasses import dataclass
from enum import Enum
from ..vdf.adapter import VDFAdapter,VDFResult

class WindowError(RuntimeError):pass
class WindowPhase(Enum):IDLE="idle";RUNNING="running";CLOSED="closed";VERIFIED="verified";ABANDONED="abandoned"

@dataclass(frozen=True)
class WindowRecord:
    record_id:bytes
    certified_time:int|None=None

@dataclass(frozen=True)
class WindowCandidate:
    count:int
    challenge:bytes
    result:VDFResult
    records:tuple[WindowRecord,...]

class EvaluationWindow:
    def __init__(self,adapter:VDFAdapter):self.adapter=adapter;self.phase=WindowPhase.IDLE;self._clear()
    def _clear(self):self.challenge=None;self.count=None;self.iterations=None;self._records=[]
    def start(self,challenge,count,iterations):
        if self.phase is not WindowPhase.IDLE:raise WindowError("window is not idle")
        if not isinstance(challenge,bytes) or len(challenge)!=32:raise WindowError("challenge must be 32 bytes")
        if not isinstance(count,int) or isinstance(count,bool) or not 0<=count<2**64:raise WindowError("count must be uint64")
        if not isinstance(iterations,int) or isinstance(iterations,bool) or iterations<1:raise WindowError("iterations must be positive")
        self.challenge=challenge;self.count=count;self.iterations=iterations;self.phase=WindowPhase.RUNNING
    def register(self,record_id,certified_time=None):
        if self.phase is not WindowPhase.RUNNING:raise WindowError("registration window is not running")
        if not isinstance(record_id,bytes) or len(record_id)!=32:raise WindowError("record_id must be 32 bytes")
        if certified_time is not None and (not isinstance(certified_time,int) or isinstance(certified_time,bool) or not 0<=certified_time<2**64):raise WindowError("certified_time must be uint64 or null")
        r=WindowRecord(record_id,certified_time);self._records.append(r);return r
    def evaluate_and_close(self):
        if self.phase is not WindowPhase.RUNNING:raise WindowError("window is not running")
        try:result=self.adapter.evaluate(self.challenge,self.iterations)
        except Exception:
            self.phase=WindowPhase.ABANDONED;raise
        self.phase=WindowPhase.CLOSED
        records=tuple(sorted(self._records,key=lambda r:(r.certified_time if r.certified_time is not None else 2**64,r.record_id)))
        return WindowCandidate(self.count,self.challenge,result,records)
    def verify(self,candidate):
        if self.phase is not WindowPhase.CLOSED:raise WindowError("window is not closed")
        if candidate.count!=self.count or candidate.challenge!=self.challenge:return False
        ok=self.adapter.verify(candidate.challenge,candidate.result)
        if ok:self.phase=WindowPhase.VERIFIED
        return ok
    def reset_after_verified(self):
        if self.phase is not WindowPhase.VERIFIED:raise WindowError("candidate is not verified")
        self._clear();self.phase=WindowPhase.IDLE
