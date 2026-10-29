# TEP-TRANSPORT-v2.2-COMPAT

Status: FROZEN COMPATIBILITY PROFILE for v0.2.0-rc1.

Compatibility oracle: the imported 12-file v2.2 baseline, which is SHA-256 identical to the observed /opt/hashburst-tep/tep production tree. Production entry point: tep.hb_tep_runtime_v220.

## UDP frame

The deployed carrier uses a 36-byte header followed by the protected payload.

| Offset | Size | Field |
|---:|---:|---|
| 0 | 4 | TEP magic and generation marker |
| 4 | 1 | version |
| 5 | 1 | packet type |
| 6 | 16 | compatibility wire node field |
| 22 | 12 | transport nonce |
| 34 | 2 | payload length |
| 36 | variable | protected payload |

Frozen packet assignments:
- heartbeat 0x01
- APP request 0x20
- APP response 0x21
- APP error 0x22
- relay request 0x23
- relay response 0x24

Frozen base values:
- transport version 2
- UDP listen port 47777
- status port 47778
- heartbeat interval 10 seconds
- header size 36 bytes

No compatibility-mode implementation may silently renumber or reinterpret these fields.

## Security compatibility

The v2.2 secure APP path uses the deployed authenticated peer-key agreement and authenticated payload-protection behavior. v0.2.0-rc1 MUST preserve the observed security semantics and fail closed when required authenticated peer material is unavailable. Production secrets are never copied into the repository or conformance fixtures.

## Identity

The 16-byte wire node field is a compatibility locator, not a globally collision-free canonical identity. HB-TEP-APP/1 additionally carries node_id and peer_id and validates these against the authenticated registered peer.

Stable identity, logical ledger address and mutable network endpoint remain separate concepts.

## Discovery and heartbeat

Production uses its blockchain-derived peer registry as primary source with peers.json bootstrap/fallback. Authenticated heartbeat may refresh mutable endpoint coordinates. Stale online state expires according to deployed freshness rules.

Heartbeat timestamp and transport nonce/counter state MUST NOT be interpreted as TEP Proof of History.

## APP, relay and HA

The packet assignments above are frozen. APP processing requires authenticated registered peer identity. Replay checking precedes protected service dispatch where implemented. Relay behavior is policy constrained and does not grant identity authority to a relay.

The HA runtime extends application services without changing the base heartbeat packet number or frame format. Deployed loopback APIs in the 47778/47780/47781 range are operational local interfaces, not UDP-frame fields.

## Conformance gate

A replacement implementation earns TEP-v2.2-COMPAT only after fixtures prove exact frame compatibility, frozen packet assignments, identity handling, heartbeat behavior, replay rejection, direct/authorized relay behavior and malformed-frame rejection using synthetic test identities only.
