"""CG-WESO-v1 adapter backed by the optional chiavdf package.

This module implements complete evaluation and verification only. It does not
claim support for per-iteration progress observation.
"""
from .adapter import VDFAdapter,VDFResult,VDFError

INITIAL_FORM=b"\x08"+b"\x00"*99
FORM_SIZE=100
DISCRIMINANT_BITS=1024

class CGWesoV1(VDFAdapter):
    suite_id="CG-WESO-v1"
    def _lib(self):
        try:
            import chiavdf
        except ImportError as e:
            raise VDFError("CG-WESO-v1 requires the optional chiavdf package") from e
        return chiavdf
    def _validate(self,challenge,iterations):
        if not isinstance(challenge,bytes) or len(challenge)!=32:raise VDFError("challenge must be 32 bytes")
        if not isinstance(iterations,int) or isinstance(iterations,bool) or iterations<1:raise VDFError("iterations must be positive")
    def evaluate(self,challenge,iterations):
        self._validate(challenge,iterations);lib=self._lib()
        blob=lib.prove(challenge,INITIAL_FORM,DISCRIMINANT_BITS,iterations,"")
        if not isinstance(blob,bytes) or len(blob)!=2*FORM_SIZE:raise VDFError("unexpected chiavdf proof encoding")
        return VDFResult(blob[:FORM_SIZE],blob[FORM_SIZE:],iterations)
    def verify(self,challenge,result):
        if not isinstance(result,VDFResult):return False
        try:self._validate(challenge,result.iterations);lib=self._lib()
        except VDFError:return False
        if len(result.output)!=FORM_SIZE or len(result.proof)!=FORM_SIZE:return False
        try:
            d=lib.create_discriminant(challenge,DISCRIMINANT_BITS)
            return bool(lib.verify_wesolowski(str(d),INITIAL_FORM,result.output,result.proof,result.iterations))
        except Exception:return False
