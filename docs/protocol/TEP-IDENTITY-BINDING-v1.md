# Signed identity binding and rotation v0.2.0-rc1

Status: RC1 project design.

A binding statement cryptographically associates one canonical PeerIdentity with its v2.2 compatibility identifiers inside one TEP network namespace.

Binding statement:

    [1, network_id, sequence, identity, legacy_binding]

Signature message:

    "HB-TEP-IDENTITY-BINDING-v1" || 0x00 || deterministic-CBOR(statement)

The statement is signed with the Ed25519 signing key contained in the same canonical identity. The legacy X25519 public key must equal the canonical transport public key.

The sequence is uint64 and is intended to be monotonically controlled by the identity registry. Registry state and anti-replay enforcement are a separate component.

Identity rotation requires two independent facts:

1. the next binding is validly signed by the next identity;
2. the previous identity signs a continuity statement authorizing exactly that next binding digest at exactly the next sequence.

Rotation statement:

    [1, network_id, sequence, previous_identity_id, next_binding_digest]

Signature message:

    "HB-TEP-IDENTITY-ROTATION-v1" || 0x00 || deterministic-CBOR(rotation_statement)

The RC1 verifier requires sequence == previous_sequence + 1. It rejects network substitution, skipped/replayed sequence, wrong previous identity, altered next binding and self-equivalent rotation.

This continuity mechanism prevents a replacement registry entry signed only by an attacker-controlled new identity from being interpreted as an authorized rotation.

Recovery from loss of the previous signing key is deliberately not defined here. That requires a separate federation/recovery policy and must not be implemented as an unsigned bypass.

No private key is serialized in either statement.
