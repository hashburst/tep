# TEP v2.2 discovery interoperability adapter

Status: RC1 compatibility gate.

The immutable v2.2 implementation has two materially different receive paths.

APP and relay packets are fail-closed: the 16-byte wire locator must resolve to exactly one registered peer with X25519 key and stable peer_id, decryption must authenticate, the APP envelope identity must match that peer, and only then may the runtime update the observed IP/port.

Legacy heartbeat processing is intentionally more permissive for backward compatibility. It may resolve by node header or source IP and may dynamically create a peer before payload authentication.

RC1 MUST NOT elevate that permissive legacy discovery behavior into canonical identity authority.

LegacyV22ReachabilityAdapter therefore accepts only an event explicitly classified by the caller as authenticated and requires exact agreement with the verified RC1 registry for:

- full node_id, not the 16-byte wire truncation;
- stable peer_id;
- X25519 public key.

The endpoint is then validated as an IP literal and port.

The adapter returns canonical identity_id and validated transport coordinates. It deliberately does not create SignedReachability and does not fabricate an Ed25519 signature that the v2.2 packet never carried.

A later runtime integration may use this result as authenticated compatibility reachability with provenance marked v2.2. Native RC1 peers should use SignedReachability directly.

No production daemon or immutable legacy source is modified by this gate.
