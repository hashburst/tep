# End-to-end ledger orchestration v0.2.0-rc1

Status: RC1 integration profile.

The orchestrator connects already specified components without taking custody of validator private keys.

Pipeline:

    previous finalized state
    -> exact next count
    -> PoH challenge
    -> VDF evaluation window
    -> record registration
    -> VDF verification
    -> canonical block assembly
    -> exact finality vote message
    -> externally supplied Ed25519 votes
    -> QC verification
    -> finalized checkpoint
    -> canonical recovery

The orchestrator never receives an externally asserted AcceptedBlock for promotion. prepare() constructs the block from the previous ledger state and a verified local VDF result.

Validator signing remains outside the orchestrator. prepare() exposes the exact vote_message. A validator agent, HSM integration or synthetic test signer may sign that byte string. The protocol layer receives only validator_id and signature.

Duplicate record IDs are rejected before VDF evaluation.

A quorum failure, signature replay from another prepared block, block mismatch or QC mismatch fails before finalized persistence.

The current integration tests use DeterministicTestVDF for speed and isolation. CG-WESO has its own runtime-conformance gate and uses the same adapter boundary. A separate integration gate must exercise this orchestration with CG-WESO before RC1 release qualification.
