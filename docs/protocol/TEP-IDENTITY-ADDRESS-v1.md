# TEP peer identity and addressing v0.2.0-rc1

Status: RC1 project design constrained by the canonical v2.2 production baseline and patent traceability.

The v2.2 runtime exposes distinct concepts:

- node_id: administrative/stable node label used by the TEP registry and APP envelope;
- peer_id: stable peer identifier used by HB-TEP-APP/1 and relay lookup;
- X25519 public key: transport key used for authenticated shared-key derivation;
- 16-byte wire node field: node_id encoded as ASCII, truncated to 16 bytes and zero padded;
- IP and UDP port: mutable transport coordinates updated only after authenticated traffic.

The 16-byte wire field is not collision-free identity. The v2.2 runtime already resolves it only when the registry match is unique.

RC1 therefore does not equate any legacy identifier with the new ledger address.

Canonical identity v1 is:

    I = [1, signing_public_key, transport_public_key]

where both public keys are exactly 32 bytes.

    identity_id =
      SHA3-256("HB-TEP-IDENTITY-v1" || 0x00 || deterministic-CBOR(I))

The signing key is reserved for cryptographic identity assertions and protocol signatures. The transport key is the X25519-compatible public key used by the encrypted transport profile. Private keys are never part of the identity object or ledger address.

The network-scoped ledger address is:

    tep_address =
      SHA3-256("HB-TEP-ADDRESS-v1" || 0x00 || network_id || identity_id)

This separates stable cryptographic identity from network namespace.

LegacyBinding records interoperability metadata:

    [1, identity_id, node_id, peer_id, x25519_public_key]

A valid binding requires the legacy X25519 public key to equal the canonical identity transport public key. node_id and peer_id remain compatibility identifiers; they are not silently redefined as identity_id.

IP address and UDP port are deliberately excluded from canonical identity and ledger addressing because v2.2 permits authenticated endpoint updates.

The exact authorization/signature format for publishing or rotating a LegacyBinding is not frozen by this document and requires a separate identity-binding decision. No production key migration is performed by this module.
