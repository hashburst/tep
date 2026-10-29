# TEP identity registry persistence v0.2.0-rc1

Status: RC1 restart-safety gate.

The durable registry is deterministic CBOR, not a Python object dump.

Document:

    [1, network_id, entries]

Each entry contains only public protocol state:

    [sequence, signing_public_key, transport_public_key,
     utf8(node_id), utf8(peer_id), binding_signature]

Entries are sorted by canonical identity_id before serialization. Private keys, IP addresses, UDP ports and process-local state are never persisted here.

Recovery decodes only the frozen restricted deterministic-CBOR subset and reconstructs every PeerIdentity, LegacyBinding and BindingStatement. Every entry is then admitted through IdentityRegistry.bootstrap(), which re-verifies its Ed25519 signature and all uniqueness constraints. The reconstructed registry must serialize byte-identically to the source document.

Persistence uses a sibling temporary file, file flush and fsync, os.replace, then best-effort directory fsync. A failure before replace removes the temporary file and preserves the previous finalized registry bytes.

This gate demonstrates deterministic restart recovery and injected pre-replace atomicity. It does not claim physical power-loss durability across every filesystem or storage controller.
