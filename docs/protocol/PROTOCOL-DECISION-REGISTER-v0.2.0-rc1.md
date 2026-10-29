# TEP v0.2.0-rc1 Protocol Decision Register

Status: RC1 DESIGN FREEZE CANDIDATE

The evidence class states where a requirement comes from. The selected design states what this project chooses. A project choice is never described as a patent requirement.

| ID | Subject | Evidence class | Selected RC1 design | State |
|---|---|---|---|---|
| PDR-001 | Genesis B0 | PROJECT-DESIGN | Versioned deterministic genesis descriptor; C0=0; H0=SHA3-256 over domain-separated deterministic CBOR genesis. | RESOLVED |
| PDR-002 | Canonical encoding | PROJECT-DESIGN | RFC 8949 core deterministic CBOR; fixed arrays; definite lengths; no floats. | RESOLVED |
| PDR-003 | Progressive Cn | PATENT-MANDATED | Unsigned 64-bit strictly increasing count. | RESOLVED |
| PDR-004 | Exact increment | PROJECT-DESIGN | Cn=C(n-1)+1; halt before uint64 exhaustion. | RESOLVED |
| PDR-005 | Recursive prior state | DESCRIPTION-DERIVED | An contains H(n-1) and block_id(n-1). | RESOLVED |
| PDR-006 | Additional input An | PROJECT-DESIGN constrained by patent model | Domain-separated digest of network_id, Cn, H(n-1), prior block_id and VDF parameter hash. Current BDn is excluded because it is collected during evaluation. | RESOLVED |
| PDR-007 | Sequential evaluation | PATENT-MANDATED for claim-5 profile | Predetermined sequential repeated-squaring evaluation. | RESOLVED |
| PDR-008 | Concrete VDF | PROJECT-DESIGN constrained by claim 6 | CG-WESO-v1: repeated squaring in an imaginary-quadratic class group with Wesolowski proof. Independent cryptographic review required before mainnet. | RESOLVED FOR RC1 |
| PDR-009 | Evaluation parameter N | PROJECT-DESIGN constrained by claim 5 | TEST 64; CONFORMANCE 4096; PILOT 1,000,000. Parameter is committed by vdf_params_hash. | RESOLVED FOR RC1 |
| PDR-010 | Verification relation | PATENT-MANDATED for claim-6 profile | Verification must succeed and measured tv must be lower than tH for the selected conformance profile. | RESOLVED |
| PDR-011 | Registration window | PATENT-MANDATED | Record binds to the active block and latest completed VDF iteration. | RESOLVED |
| PDR-012 | Canonical rdp | PATENT-PERMITTED plus PROJECT-DESIGN | Fixed deterministic record core, SHA3-256 record_id and protection field. | RESOLVED |
| PDR-013 | Certified TSA time | PATENT-PERMITTED | Nullable certified-time field; optional profile. | RESOLVED |
| PDR-014 | Same-block ordering | PATENT-PERMITTED plus PROJECT-DESIGN | iteration_index, then certified_time when present, then record_id as deterministic tie-breaker. | RESOLVED |
| PDR-015 | Record protection | PATENT-PERMITTED plus security design | Ed25519 COSE_Sign1 required for normative RC1 records; null only for declared legacy/import profile. | RESOLVED |
| PDR-016 | Prior-ledger hash/reference | PATENT-PERMITTED | prior_block_id is mandatory in normative RC1 record core and request context. | RESOLVED |
| PDR-017 | Privacy pruning | PATENT-PERMITTED plus PROJECT-DESIGN | Prune non-local record metadata only after finality while retaining commitments and ordering evidence. | RESOLVED |
| PDR-018 | Competing blocks | PROJECT-DESIGN | Eligible candidates share predecessor/count/parameters; smallest block_id is deterministic RC1 tie-breaker. Not a Byzantine-consensus claim. | RESOLVED FOR RC1 |
| PDR-019 | Quorum/dissemination | PROJECT-DESIGN | Versioned federation validator set; finality certificate threshold floor(2m/3)+1. | RESOLVED FOR RC1 |
| PDR-020 | Crash recovery | PROJECT-DESIGN | Atomic finalized checkpoints; verify-forward recovery; incomplete VDF state is never accepted ledger state. | RESOLVED |
| PDR-021 | v2.2 carrier | PRODUCTION-DERIVED | Frozen TEP-v2.2-COMPAT carrier remains available. | FROZEN |
| PDR-022 | Identity migration | PRODUCTION-DERIVED | Preserve existing identity and peer state; ledger state stored separately. | FROZEN |
| PDR-023 | Transport counters vs PoH | PATENT/PRODUCTION BOUNDARY | Transport state is never imported as ledger PoH state. | FROZEN |
| PDR-024 | Solana semantics | PROJECT GUARDRAIL | No Solana-specific semantics are imported by analogy. | FROZEN |

## External standards used by project design

- FIPS 202 for SHA3-256.
- RFC 8949 section 4.2.1 for deterministic CBOR requirements.
- RFC 9052 for COSE_Sign1 structure.
- Wesolowski VDF literature for the selected RC1 proof construction.

These standards support project implementation choices. They do not change the scope of the cited TEP patents.

## Freeze conditions

PDR-008, PDR-009, PDR-018 and PDR-019 are resolved for RC1 experimentation, not for mainnet. Mainnet freeze requires independent cryptographic review, performance benchmarks, adversarial interoperability tests and a separate mainnet decision record.

## PDR-025: VDF progress observation

Subject: binding a registration to the active VDF evaluation without inventing unavailable intermediate states.

Evidence class: PROJECT-DESIGN constrained by claim 1 registration-window semantics and the patent-permitted same-block ordering profiles.

Finding: claim 1 requires a registration received during the evaluation interval to be associated with the block whose hash is being evaluated. The traced claim does not require a per-request VDF iteration index. Claims 3 and 4 separately provide same-block ordering profiles. The selected chiavdf Python interface exposes complete evaluation and verification but not the main-loop intermediate forms as an iterator.

RC1 decision: RESOLVED.

The normative CG-WESO-v1 profile binds a registration to the active evaluation instance and block count while that evaluation is RUNNING. It MUST NOT synthesize iteration_index or iteration_state_digest. Same-block deterministic ordering for this profile uses certified_time when the certified-time profile is active, followed by record_id as a deterministic tie-breaker. When certified time is absent, record_id provides deterministic canonicalization only and MUST NOT be represented as evidence of physical arrival order.

The existing per-iteration marker remains an EXPERIMENTAL TEST PROFILE for DeterministicTestVDF and is not emitted by CG-WESO-v1.

Crash/restart rule: an evaluation instance that terminates without a valid final VDF result is abandoned. Its registrations are not silently moved into a completed block. Recovery restarts from the last accepted predecessor and opens a new evaluation instance.

Rationale: this satisfies the traced registration-window requirement without modifying the VDF implementation or claiming observations that the concrete evaluator does not expose.
