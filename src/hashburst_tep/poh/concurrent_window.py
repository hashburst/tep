"""Concurrent VDF evaluation window for registration during actual evaluation."""
import threading,time
from dataclasses import dataclass
from .window import WindowCandidate,WindowRecord,WindowPhase,WindowError

@dataclass(frozen=True)
class EvaluationTiming:
    started_monotonic_ns:int
    finished_monotonic_ns:int

class ConcurrentEvaluationWindow:
    def __init__(self,adapter):
        self.adapter=adapter;self.phase=WindowPhase.IDLE;self._lock=threading.Lock()
        self._started=threading.Event();self._finished=threading.Event();self._records=[]
        self.challenge=None;self.count=None;self.iterations=None;self.result=None;self.error=None;self.timing=None
    def start(self,challenge,count,iterations):
        if not isinstance(challenge,bytes) or len(challenge)!=32:raise WindowError("challenge must be 32 bytes")
        if not isinstance(count,int) or isinstance(count,bool) or not 0<=count<2**64:raise WindowError("count must be uint64")
        if not isinstance(iterations,int) or isinstance(iterations,bool) or iterations<1:raise WindowError("iterations must be positive")
        with self._lock:
            if self.phase is not WindowPhase.IDLE:raise WindowError("window is not idle")
            self.challenge=challenge;self.count=count;self.iterations=iterations
        def run():
            start_ns=time.monotonic_ns()
            with self._lock:self.phase=WindowPhase.RUNNING
            self._started.set()
            try:result=self.adapter.evaluate(self.challenge,self.iterations)
            except BaseException as e:
                with self._lock:self.error=e;self.phase=WindowPhase.ABANDONED
            else:
                end_ns=time.monotonic_ns()
                with self._lock:self.result=result;self.timing=EvaluationTiming(start_ns,end_ns);self.phase=WindowPhase.CLOSED
            finally:self._finished.set()
        self._thread=threading.Thread(target=run,name="tep-vdf-evaluation",daemon=True);self._thread.start()
    def wait_started(self,timeout=None):
        if not self._started.wait(timeout):raise TimeoutError("VDF evaluation did not start")
    def register(self,record_id,certified_time=None):
        if not isinstance(record_id,bytes) or len(record_id)!=32:raise WindowError("record_id must be 32 bytes")
        if certified_time is not None and (not isinstance(certified_time,int) or isinstance(certified_time,bool) or not 0<=certified_time<2**64):raise WindowError("certified_time must be uint64 or null")
        with self._lock:
            if self.phase is not WindowPhase.RUNNING:raise WindowError("registration window is not running")
            r=WindowRecord(record_id,certified_time);self._records.append(r);return r
    def close(self,timeout=None):
        if not self._finished.wait(timeout):raise TimeoutError("VDF evaluation did not finish")
        with self._lock:
            if self.phase is WindowPhase.ABANDONED:raise self.error
            if self.phase is not WindowPhase.CLOSED:raise WindowError("window is not closed")
            records=tuple(sorted(self._records,key=lambda r:(r.certified_time if r.certified_time is not None else 2**64,r.record_id)))
            return WindowCandidate(self.count,self.challenge,self.result,records)
    def verify(self,candidate):
        with self._lock:
            if self.phase is not WindowPhase.CLOSED:raise WindowError("window is not closed")
            if candidate.count!=self.count or candidate.challenge!=self.challenge:return False
        ok=self.adapter.verify(candidate.challenge,candidate.result)
        if ok:
            with self._lock:self.phase=WindowPhase.VERIFIED
        return ok
