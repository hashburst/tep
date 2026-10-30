# CG-WESO-v1 integration boundary

Status: EXPERIMENTAL RC1

CG-WESO-v1 uses repeated squaring in an imaginary-quadratic class group and a Wesolowski proof through the optional chiavdf implementation.

This is a project implementation choice. It is not identified as a construction required by EP4169233B1.

The adapter uses a 1024-bit discriminant and the standard 100-byte initial class-group form used by the selected implementation. Evaluation returns a 100-byte output form and a 100-byte simple Wesolowski proof.

The adapter currently implements complete evaluation and verification. It does not implement per-iteration progress observation.

This distinction matters because the RC1 mock state machine can expose every deterministic test iteration. The public Python chiavdf interface does not expose the main-loop intermediate class-group forms as an iterator. The project MUST NOT manufacture such observations by repeatedly restarting complete VDF evaluations and call that equivalent to native progress.

Until a real progress contract is selected, CG-WESO-v1 is tested independently from record binding.

Acceptable future designs are:

1. a native progress callback from the VDF evaluator that reports a completed iteration and canonical group element;
2. a separately authenticated progress service tied to the same evaluator state;
3. a protocol profile that does not require an intra-block VDF-state marker and uses another patent-permitted same-block ordering method.

The choice requires a new Protocol Decision Register entry before integration with the PoH recording window.

Conformance requires successful proof verification, rejection of corrupted output, rejection of corrupted proof, rejection of a wrong iteration count and measured verification time lower than evaluation time for the conformance profile.
