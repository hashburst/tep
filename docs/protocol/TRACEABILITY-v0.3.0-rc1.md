# v0.3.0-rc1 Traceability Matrix

| Requirement | Protocol rule | Implementation | Conformance |
| --- | --- | --- | --- |
| Versioned federation authority | F-001 | `FederationState`, `ValidatorSet` | validator-set and transition tests |
| Quorum finality | F-002 | v0.2 QC verifier with active v0.3 validator set | v0.2 finality suite and v0.3 threshold tests |
| Certified membership lifecycle | F-003 | `MembershipProposal`, `apply_membership` | transition, stale proposal, revocation tests |
| Vote context binding | F-004 | v0.2 `QuorumCertificate.message` | v0.2 tamper tests |
| Equivocation handling | F-005 | `VoteKey`, `EquivocationTracker` | conflicting vote test |
| Partition safety | F-006 | `partition_has_quorum` | 7/5, 7/4 and 4/2 tests |
| Recovery and rejoin | F-007 | `RecoveryCursor` and v0.2 verify-forward recovery | forward-progress and v0.2 recovery tests |
| Federation/Sovereignty separation | S-001 | `SovereigntyPolicy` independent of validator membership | permission tests |
| Versioned sovereignty policy | S-002 | policy version and digest | deterministic digest test |
| Fail closed | S-003 | explicit permission predicates and policy validation | invalid policy tests |

The patent-derived TEP ledger and ordering foundation remains in the v0.2.0-rc1 baseline. The governance and sovereignty rules above are v0.3 release-candidate protocol decisions and are not presented as retroactive patent claims.
