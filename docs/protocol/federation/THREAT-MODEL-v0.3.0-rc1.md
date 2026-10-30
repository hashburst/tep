# TEP Federation Threat Model v0.3.0-rc1

## Security objectives

The federation must preserve authenticated membership, deterministic quorum evaluation, finality safety, replay resistance, identity continuity and verifiable recovery.

## Considered faults

The release candidate tests Byzantine voting behavior, duplicate votes, equivocation, stale validator-set versions, forged voter identities, replayed certificates, minority partitions, delayed messages, node restart, stale local state and corrupted unfinalized state.

The model assumes Ed25519 private keys remain confidential and cryptographic verification is correct. Key compromise is handled by certified suspension, retirement or revocation after detection; compromise before revocation can authorize votes attributable to that validator.

## Safety boundary

A node never accepts a quorum certificate from vote count alone. It verifies federation identifier, validator-set version, voter membership, signature, uniqueness and proposal binding.

A minority partition cannot finalize new federation state.

The release candidate does not claim protection against compromise of a quorum of active validator keys.

## Liveness boundary

Safety takes precedence over liveness. When no partition has quorum, finality stops until sufficient authenticated validators can communicate again.

## Test obligations

Conformance tests cover threshold boundaries, duplicate-vote rejection, equivocation detection, stale-set rejection, partition behavior, certified membership changes, restart recovery and catch-up from a finalized checkpoint.
