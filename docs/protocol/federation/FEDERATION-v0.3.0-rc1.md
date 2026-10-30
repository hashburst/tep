# TEP Federation v0.3.0-rc1

## Scope

This document defines the controlled federation model for the v0.3.0 release-candidate line. It extends the v0.2.0-rc1 ledger, identity, signed record and preliminary finality primitives. It does not alter the published v0.2.0-rc1 baseline.

## Validator set

A federation state identifies a versioned validator set. Each active validator entry binds a canonical TEP peer identity, an Ed25519 verification key, a membership state and the validator-set version in which that state is effective.

Membership states are CANDIDATE, ACTIVE, SUSPENDED, RETIRED and REVOKED.

Only ACTIVE validators count toward quorum. REVOKED is terminal for the affected validator identity and key. Re-entry requires a separately authorized identity binding.

For m active validators the quorum threshold is:

q(m) = floor(2m / 3) + 1

A vote is valid only for the validator-set version named by the object being voted on.

## State transitions

CANDIDATE may become ACTIVE after a membership proposal obtains a quorum certificate from the current active validator set.

ACTIVE may become SUSPENDED, RETIRED or REVOKED through the same certified transition process.

SUSPENDED may return to ACTIVE through a new certified transition.

Membership changes become effective only after the corresponding transition is committed in finalized federation state. A proposal cannot change the validator set used to certify itself.

## Finality

A finality vote binds at least the federation identifier, validator-set version, ledger height or checkpoint count, proposal digest and voter identity.

A quorum certificate is valid when it contains valid, distinct votes from at least q(m) ACTIVE validators of the referenced validator-set version and every vote binds the same proposal digest.

A validator must not issue two finality votes for different proposal digests at the same federation identifier, validator-set version and height.

A finalized checkpoint is immutable within the same federation history. A node presented with a conflicting certificate at the same height records an equivocation fault and does not choose a branch by local preference.

## Network partitions

A partition without quorum cannot create finality. A partition with quorum may continue to finalize under the current validator-set version.

After reconnection, nodes verify certificates from their last finalized checkpoint forward. Unfinalized local candidates may be discarded. Finalized conflicting certificates are treated as a safety violation requiring operator review; they are not resolved by the v0.2.0-rc1 lexicographic candidate rule.

## Recovery and rejoin

A rejoining node starts from its last verified finalized checkpoint, obtains later federation state and ledger material from authenticated peers, verifies every transition and quorum certificate, and only then resumes voting.

No peer may replace the node's local private identity during catch-up.
