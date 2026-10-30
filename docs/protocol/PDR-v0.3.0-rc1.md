# Protocol Decision Register v0.3.0-rc1

## F-001 Versioned validator sets
Federation finality is evaluated against an explicit validator-set version.

## F-002 Quorum
For m ACTIVE validators, q(m) = floor(2m / 3) + 1.

## F-003 Membership activation
A membership change is certified by the current validator set and becomes effective only after finalization.

## F-004 Vote binding
Votes bind federation, validator-set version, height and proposal digest.

## F-005 Equivocation
Conflicting votes by one validator for the same federation, validator-set version and height are evidence of equivocation and are rejected from normal finality processing.

## F-006 Partition safety
A partition without quorum cannot finalize new state.

## F-007 Recovery
Rejoin verifies finalized state forward from the last locally verified finalized checkpoint.

## S-001 Federation and sovereignty
Federation authority and access to protected sovereign payloads are separate capabilities.

## S-002 Versioned sovereignty policy
Authorization decisions bind a sovereignty-domain identifier and policy version.

## S-003 Fail closed
If the required policy or its finalized provenance cannot be verified, the protected operation is denied.

## Compatibility
These decisions extend v0.2.0-rc1. They do not change the published v0.2.0-rc1 tag or reinterpret its preliminary finality primitives as a complete Byzantine consensus protocol.
