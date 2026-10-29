"""Stable adapter contract between TEP PoH and a concrete VDF suite."""
from abc import ABC,abstractmethod
from dataclasses import dataclass

class VDFError(RuntimeError): pass

@dataclass(frozen=True)
class VDFResult:
    output: bytes
    proof: bytes
    iterations: int

class VDFAdapter(ABC):
    suite_id: str
    @abstractmethod
    def evaluate(self,challenge:bytes,iterations:int)->VDFResult: raise NotImplementedError
    @abstractmethod
    def verify(self,challenge:bytes,result:VDFResult)->bool: raise NotImplementedError
    def resume(self,challenge:bytes,iterations:int,checkpoint:bytes)->VDFResult:
        raise VDFError("resume is not supported by this adapter")
