# Federation finality profile v0.2.0-rc1

Status: RC1 PROJECT DESIGN

This federation profile is not claimed as a requirement of EP4169233B1. It implements PDR-019 so that a local block cannot become finalized merely because a caller supplies an opaque digest.

## Validator set

A validator set has a monotonically managed uint64 version and one or more validators. Each validator has a 32-byte validator_id and a raw 32-byte Ed25519 public key.

Canonical validator-set order is ascending validator_id. Duplicate validator IDs and duplicate public keys are rejected.

The validator-set digest is domain-separated SHA3-256 over deterministic CBOR containing schema version, set version and canonical validator entries.

## Finality vote

Every validator signs exactly:

    FINALITY_VOTE_DOMAIN ||
    CBOR([
      1,
      validator_set_version,
      validator_set_digest,
      network_id,
      count,
      block_id
    ])

This binds the vote to one network, one validator-set version and content, one progressive block count and one exact block identifier.

Private keys are not part of the protocol object or repository.

## Quorum certificate

The RC1 threshold is:

    floor(2m/3) + 1

implemented equivalently as:

    floor(2m/3) + 1 = floor((2m)/3) + 1

for m validators.

A QC is valid only if all counted signatures are valid Ed25519 signatures by distinct members of the exact validator set and the number of valid distinct votes reaches the threshold. Unknown validators, duplicate votes, invalid signatures, set mismatches and block mismatches fail closed.

The QC digest commits the canonical ordered vote set and is stored in the finalized checkpoint.

## Finalization gate

finalize_verified_block verifies that the QC identifies the exact network, count and block_id and verifies the QC against the supplied validator set before calling persist_finalized.

This module assumes the supplied AcceptedBlock has already passed the PoH and block-assembly gates. A later orchestration layer must preserve that sequencing and must not construct AcceptedBlock objects from unverified external data.
