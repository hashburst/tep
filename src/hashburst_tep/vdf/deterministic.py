"""Deterministic test adapter.

This adapter is NOT a cryptographic VDF. It exists only to exercise the PoH
state machine with reproducible sequential states and verification behavior.
"""
from hashlib import sha3_256
from .adapter import VDFAdapter,VDFResult,VDFError

_DOMAIN=b"HB-TEP-TEST-VDF-v1\x00"

class DeterministicTestVDF(VDFAdapter):
    suite_id="TEST-DETERMINISTIC-v1"
    def _validate(self,challenge,iterations):
        if not isinstance(challenge,bytes) or len(challenge)!=32: raise VDFError("challenge must be 32 bytes")
        if not isinstance(iterations,int) or isinstance(iterations,bool) or iterations<1: raise VDFError("iterations must be positive")
    def states(self,challenge,iterations):
        self._validate(challenge,iterations);state=sha3_256(_DOMAIN+challenge).digest()
        for i in range(1,iterations+1):
            state=sha3_256(_DOMAIN+i.to_bytes(8,"big")+state).digest();yield i,state
    def evaluate(self,challenge,iterations):
        state=None
        for _,state in self.states(challenge,iterations):pass
        proof=sha3_256(_DOMAIN+b"proof"+challenge+iterations.to_bytes(8,"big")+state).digest()
        return VDFResult(state,proof,iterations)
    def verify(self,challenge,result):
        if not isinstance(result,VDFResult):return False
        try:expected=self.evaluate(challenge,result.iterations)
        except VDFError:return False
        return expected==result
