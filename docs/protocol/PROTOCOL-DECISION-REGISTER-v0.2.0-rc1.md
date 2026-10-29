# TEP v0.2.0-rc1 Protocol Decision Register

Status: PRE-NORMATIVE

This register separates patent requirements from implementation choices. A decision marked OPEN is not part of the protocol.

## Classification

PATENT-MANDATED means required by the traced granted claims for the stated profile.

PATENT-PERMITTED means described or allowed by the patent material but not mandatory in every claim profile.

PRODUCTION-DERIVED means required only for compatibility with the observed TEP v2.2 runtime.

PROJECT-DESIGN means a new engineering choice that must be justified, tested and approved before specification freeze.

## Decisions

| ID | Subject | Evidence | Classification | Current decision |
| --- | --- | --- | --- | --- |
| PDR-001 | Genesis block B0 | The description starts the recursive sequence from a source block but does not freeze a binary genesis construction. | PROJECT-DESIGN | OPEN |
| PDR-002 | Canonical block encoding | Claims define semantic fields and relationships, not a final byte encoding. | PROJECT-DESIGN | OPEN |
| PDR-003 | Progressive count Cn | Claim 1 requires a progressive count; claim 2 uses its increasing value for ordering. | PATENT-MANDATED | C(n+1) > Cn. Exact step remains OPEN. |
| PDR-004 | Exact count increment | No traced claim requires increment by exactly one. | PROJECT-DESIGN | OPEN |
| PDR-005 | Recursive prior state | Description models Hn from H(n-1) and optional additional values. | PATENT-PERMITTED / DESCRIPTION-DERIVED | Preserve recursive prior-state dependency. Exact encoding OPEN. |
| PDR-006 | Additional input An | Description permits additional values but does not freeze their set. | PROJECT-DESIGN constrained by patent model | OPEN |
| PDR-007 | Sequential evaluation | Claims 1 and 5 require predetermined sequential work; claim 5 requires iterative dependency on the previous result. | PATENT-MANDATED for claim-5 profile | REQUIRED |
| PDR-008 | Concrete VDF | Claim 6 requires evaluation/verification algorithms of a VDF in its dependent profile but does not freeze a concrete construction. | PROJECT-DESIGN constrained by claim 6 | OPEN |
| PDR-009 | Evaluation parameter N | Claim 5 requires a predetermined iteration count in its profile but not a universal numeric value. | PROJECT-DESIGN constrained by claim 5 | OPEN |
| PDR-010 | Verification relation | Claim 6 requires verification faster than evaluation. | PATENT-MANDATED for claim-6 profile | Require tv < tH. Measurement profile OPEN. |
| PDR-011 | Registration window | Claim 1 binds a transmission to the block whose hash is being calculated when registration is requested. | PATENT-MANDATED | REQUIRED |
| PDR-012 | Transmission record rdp | Claims 9-11 define dependent record-information profiles. | PATENT-PERMITTED / profile-dependent | Base canonical fields OPEN. |
| PDR-013 | Certified TSA time | Claim 8 adds certified time as a dependent profile. | PATENT-PERMITTED / profile-dependent | OPTIONAL PROFILE |
| PDR-014 | Same-block ordering | Claims 3 and 4 provide timestamp-based and associated-hash ordering profiles. | PATENT-PERMITTED / profile-dependent | OPEN profile selection |
| PDR-015 | Record protection | Claim 10 provides recipient protection and/or sender authentication. | PATENT-PERMITTED; security design also required | OPEN exact representation |
| PDR-016 | Prior-ledger hash in request | Claim 11 adds the last-ledger-block hash at transmission time. | PATENT-PERMITTED / profile-dependent | OPEN |
| PDR-017 | Privacy pruning | Claim 12 removes information unrelated to the local sender/recipient role. | PATENT-PERMITTED / profile-dependent | OPEN commitment and pruning representation |
| PDR-018 | Competing blocks | No traced claim freezes a distributed fork-choice rule. | PROJECT-DESIGN | OPEN |
| PDR-019 | Quorum and dissemination | No traced claim freezes quorum or broadcast mechanics. | PROJECT-DESIGN | OPEN |
| PDR-020 | Crash recovery | Patent semantics require continuity but do not freeze software checkpoint format. | PROJECT-DESIGN | OPEN |
| PDR-021 | v2.2 transport carrier | Observed production runtime defines the compatibility wire profile. | PRODUCTION-DERIVED | FROZEN in TEP-TRANSPORT-v2.2-COMPAT |
| PDR-022 | Identity migration | Production identities persist outside the repository. | PRODUCTION-DERIVED | MUST preserve existing identity and state |
| PDR-023 | Transport counters versus PoH | Patent PoH is ledger evaluation/order; v2.2 transport counters are carrier state. | PATENT / PRODUCTION boundary | MUST remain separate |
| PDR-024 | Solana semantics | No traced TEP patent requirement establishes Solana-specific protocol semantics. | PROJECT GUARDRAIL | MUST NOT import by analogy |

## Freeze rule

An OPEN item may become normative only after its evidence class, selected construction, deterministic test vectors, failure behavior and migration impact are recorded. A project design must never be described as a patent requirement.
