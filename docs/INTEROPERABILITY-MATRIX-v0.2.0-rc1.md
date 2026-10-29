# TEP interoperability matrix: legacy -> production v2.2.0 -> v0.2.0-rc1

Status: initial evidence matrix. No production service was modified by this import.

| Area | Legacy evidence at node-installer commit 034d2960 | Production v2.2.0 baseline | v0.2.0-rc1 gate |
| --- | --- | --- | --- |
| Runtime lineage | hb_tep_runtime_v220.py extends the field-validated v2.1.6 transport with HA application service | Must be verified against observer 64.31.4.9 before declaring byte/runtime equivalence | Preserve v2.2 compatibility through explicit adapter/version negotiation |
| Core transport | hb_tep.py and hb_tep_runtime.py | Existing production wire behavior is compatibility baseline | No incompatible wire change without negotiated protocol version |
| APP protocol | HB-TEP-APP/1 in hb_tep_app.py and hb_tep_wire.py | Production packet assignments and capabilities must be observed/frozen from deployed daemon | Collision-free tested assignments and legacy encoder/decoder interoperability |
| Packet numbering | hb_tep_wire.py says candidate 0x20-0x3f values are not frozen production assignments | Observe real daemon constants | Never invent or silently renumber production packet types |
| HA services | ha.lease and master.status added by hb_tep_runtime_ha.py | v2.2 HA behavior is baseline where deployed | Preserve semantics or provide compatibility translation |
| Heartbeat | HA runtime states base packet numbers and heartbeat wire format remain unchanged | Observe deployed heartbeat and peer freshness | Regression fixture must decode legacy heartbeat and preserve freshness semantics |
| Replay protection | APP request path checks replay before service dispatch | Verify deployed persistence and lifetime semantics | Anti-replay mandatory and migration must not weaken legacy guarantees |
| Relay/failover | FailoverTepTransport direct plus relay path exists | Verify production rendezvous and relay policy | Preserve reachable legacy peers |
| Local IPC | HA IPC loopback 127.0.0.1:47781 with bounded JSON | Verify deployed bind, port and service exposure | Local-only by default; versioned migration if port/schema changes |
| Identity | APP carries node_id and peer_id with validation | Capture public identity format only; never export private keys | Persistent identity continuity; private key remains local |
| Service allowlist | v2.2 extends v2.1.6 allowlist process-locally | Verify deployed advertised services | Compatibility tests cover legacy service set |
| Scope boundary | v2.2 keeps project workloads outside transport | Production HashBurst scope is compatibility boundary | TEP transport/ledger separated from mining workload policy |
| TEP ledger/addressing | Not established by imported tep folder alone | Production evidence required before normative claim | TEP-LEDGER-v1 and TEP-ADDRESS-v1 only after reconstruction |
| TEP Proof of History | Not established by imported tep folder | Production/patent evidence required | TEP-POH-v1 patent-faithful; no Solana or VDF assumption |
| Upgrade/rollback | Installer/regression evidence exists outside tep folder | Production state must be inventoried read-only | Backup superseded release before upgrade; preserve identity/state |
| Mainnet | Import does not activate mainnet | No activation implied | mainnet remains disabled until roadmap gate |
| Production APPLY | Import performs no mining APPLY | No activation implied | production_apply remains false |

## Evidence rule

The legacy directory is a byte-preserving evidence copy, not an implementation workspace. New implementation belongs outside legacy. Claims about the live observer require read-only observation or exported public diagnostics; repository naming alone is not proof of deployed equivalence.
