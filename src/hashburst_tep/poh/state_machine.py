"""PoH evaluation-window state machine independent of a concrete VDF suite."""
from hashlib import sha3_256
from ..domains import POH_OUTPUT_DOMAIN
from ..encoding import uint64be
from ..vdf.adapter import VDFAdapter,VDFResult
from .model import PoHPhase,BoundRecord,PoHCandidate

class PoHStateError(RuntimeError):pass

class PoHStateMachine:
    def __init__(self,adapter:VDFAdapter):
        self.adapter=adapter;self.phase=PoHPhase.IDLE;self._reset()
    def _reset(self):
        self.challenge=None;self.count=None;self.iterations=None;self._last_index=0;self._last_state=None;self._records=[];self._result=None
    def start(self,challenge:bytes,count:int,iterations:int):
        if self.phase is not PoHPhase.IDLE:raise PoHStateError("state machine is not idle")
        if not isinstance(challenge,bytes) or len(challenge)!=32:raise PoHStateError("challenge must be 32 bytes")
        if not isinstance(count,int) or isinstance(count,bool) or not 0<=count<2**64:raise PoHStateError("count must be uint64")
        if not isinstance(iterations,int) or isinstance(iterations,bool) or iterations<1:raise PoHStateError("iterations must be positive")
        self.challenge=challenge;self.count=count;self.iterations=iterations;self.phase=PoHPhase.EVALUATING
    def advance(self,steps:int=1):
        if self.phase is not PoHPhase.EVALUATING:raise PoHStateError("not evaluating")
        if not isinstance(steps,int) or isinstance(steps,bool) or steps<1:raise PoHStateError("steps must be positive")
        target=min(self.iterations,self._last_index+steps)
        for i,state in self.adapter.states(self.challenge,target):
            if i>self._last_index:self._last_index=i;self._last_state=state
        return self._last_index
    def bind_record(self,record_id:bytes,certified_time:int|None=None):
        if self.phase is not PoHPhase.EVALUATING:raise PoHStateError("recording window is closed")
        if self._last_index<1 or self._last_state is None:raise PoHStateError("no completed iteration")
        if not isinstance(record_id,bytes) or len(record_id)!=32:raise PoHStateError("record_id must be 32 bytes")
        marker=sha3_256(POH_OUTPUT_DOMAIN+self.challenge+uint64be(self._last_index)+self._last_state).digest()
        r=BoundRecord(record_id,self._last_index,marker,certified_time);self._records.append(r);return r
    def close(self):
        if self.phase is not PoHPhase.EVALUATING:raise PoHStateError("not evaluating")
        self._result=self.adapter.evaluate(self.challenge,self.iterations);self.phase=PoHPhase.CLOSED
        ordered=tuple(sorted(self._records,key=lambda r:(r.iteration_index,r.certified_time if r.certified_time is not None else 2**64,r.record_id)))
        return PoHCandidate(self.count,self.challenge,self._result,ordered)
    def verify(self,candidate:PoHCandidate):
        if self.phase is not PoHPhase.CLOSED:raise PoHStateError("candidate is not closed")
        if candidate.challenge!=self.challenge or candidate.count!=self.count:return False
        ok=self.adapter.verify(candidate.challenge,candidate.result)
        if ok:self.phase=PoHPhase.VERIFIED
        return ok
    def reset_after_verified(self):
        if self.phase is not PoHPhase.VERIFIED:raise PoHStateError("candidate is not verified")
        self.phase=PoHPhase.IDLE;self._reset()
