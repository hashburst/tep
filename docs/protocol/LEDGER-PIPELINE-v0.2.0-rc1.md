# Ledger pipeline profile v0.2.0-rc1

This document reconciles the controlled-design draft with PDR-025.

## Record schema versions

Record schema 1 is the previously frozen deterministic test-vector schema. It contains iteration_index and iteration_state_digest and remains valid for the experimental DeterministicTestVDF profile and frozen vectors. Its bytes are not reinterpreted.

Record schema 2 is the normative CG-WESO registration-window schema:

    [
      2,
      sender_id,
      recipient_id,
      packet_id,
      sequence,
      prior_block_id,
      certified_time,
      payload_digest
    ]

It contains no synthetic VDF progress fields. record_id uses the existing RECORD_DOMAIN and commits the schema version through the first array element.

The ledger record remains:

    [RecordCore, record_id, protection]

## Verified candidate to block

A block may be assembled for acceptance only after the active VDF adapter verifies the candidate.

For a verified candidate:

    Hn = SHA3-256(
      POH_OUTPUT_DOMAIN || 0x00 ||
      An ||
      EncodeGroupElement(yN)
    )

The header, body_root and block_id use the already frozen deterministic rules.

The VDF proof remains beside BlockCore and is not included in block_id.

## Finalization boundary

Block assembly creates an accepted candidate object but does not by itself create federation finality.

A finalized checkpoint is persisted only after the caller supplies the validator-set version and quorum-certificate digest required by the federation profile.

Crash before successful atomic checkpoint persistence does not advance the finalized ledger state.

## Recovery

The finalized checkpoint file stores:

    checkpoint_id || CheckpointCore

Recovery verifies checkpoint_id before returning finalized state. Ledger-forward verification and quorum-certificate verification remain higher-layer requirements before network service activation.

## Security boundary

The pipeline does not treat a transport nonce, heartbeat timestamp, wall-clock timestamp or mock iteration state as CG-WESO PoH evidence.

Record schema 2 certified_time is nullable. If absent, record_id ordering is deterministic canonicalization only and is not physical-arrival-time evidence.
