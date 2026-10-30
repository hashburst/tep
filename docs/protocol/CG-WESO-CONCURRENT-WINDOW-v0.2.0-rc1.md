# Real CG-WESO concurrent registration gate v0.2.0-rc1

Purpose: demonstrate physical overlap between a TEP registration and an actual CG-WESO-v1 evaluation backed by chiavdf.

Test profile:

- adapter: CGWesoV1
- chiavdf: 1.2.1
- iterations: 1,000,000, the RC1 PILOT parameter
- synthetic challenge and record identifier
- no production identity, key or state

The test starts ConcurrentEvaluationWindow and waits for its worker-start handshake. It requires phase RUNNING, records a diagnostic monotonic instant, registers the record, and immediately requires the window still to be RUNNING. It then waits for chiavdf evaluation to complete, verifies the Wesolowski proof, and requires the record to be present in the resulting candidate.

The diagnostic relation required by the test is:

    evaluation_start <= registration < evaluation_finish

These monotonic values are local test observations only. They are not serialized, are not certified timestamps, are not ledger consensus inputs and are not TEP Proof of History.

This gate demonstrates the patent-traced lifecycle property that a registration can be associated with the block whose hash/VDF evaluation is in progress when the registration occurs. It does not claim that civil time is encoded in Hn and does not introduce Solana PoH semantics.

Passing this gate freezes the RC1 PoH/ledger lifecycle baseline unless a defect is subsequently demonstrated.
