# Patent-to-Protocol Traceability Matrix — TEP v0.2.0-rc1

Status: PRE-NORMATIVE. This matrix records evidence and implementation gates. It does not freeze protocol semantics.

## Evidence hierarchy

1. Granted patent text and patent-family disclosures.
2. Canonical production runtime observed on 64.31.4.9 at /opt/hashburst-tep.
3. Git-traceable legacy/current implementation imported from hashburst/node-installer commit 034d29603a5dcd4d38bbcf403c31d0d2d7eb734a.
4. Historical installer snapshot /opt/node-installer-v220-blockchainapi/tep, retained as migration evidence where divergent.

The production observer established that all 12 tracked modules under /opt/hashburst-tep are SHA-256 identical to the imported Git baseline. The running service executes python3 -m tep.hb_tep_runtime_v220. The historical installer tree contains divergent older/different copies of selected modules and is not the canonical executable baseline.

## Patent families used in this phase

- TEP foundation: US11799659B2, family of IT201800005763A1 / WO2019229612A1 / EP3804376A1.
- Secure transmission, distributed ledger and Proof of History: EP4169233B1, family of IT202000014509A1 / WO2021255630A1 / US12609828B2.
- Graph-database routing: EP4169234B1, family of IT202000014518A1 / WO2021255633A1 / US12335247B2.

These are separate patent families. TEP-PoH is reconstructed from the BitCorp secure-transmission family on its own terms. No Solana semantics are imported by name or analogy.

## Traceability matrix

| ID | Domain | Patent evidence | Production / legacy evidence | v0.2.0-rc1 requirement | Status |
| --- | --- | --- | --- | --- | --- |
| ID-01 | Identity | US11799659B2 establishes a distributed-ledger addressing model in which sender and recipient addresses are generated/represented through hashes and checked by the receiving node. | hb_tep.py maintains node_id, peer_id and registered TEP public key; APP validates source and destination against the authenticated peer. | Define stable node identity, transport cryptographic identity and application peer identity without collapsing them into one field. Preserve deployed identities during upgrade. | EVIDENCED |
| ID-02 | Identity binding | US11799659B2 requires integrity/address correspondence verification at the receiving node. | Production requires registered X25519 peer key for APP and checks envelope node_id/peer_id against authenticated peer. | TEP-IDENTITY-v1 MUST specify binding and verification rules; private keys remain node-local. | EVIDENCED |
| ADDR-01 | Addressing | US11799659B2 describes routing to addresses registered in a ledger and addresses represented by hashes rather than conventional DNS naming. | hb_tep.py describes BlockchainDNS with local blockchain peer registry as primary source and peers.json fallback/bootstrap. | TEP-ADDRESS-v1 MUST separate normative TEP address semantics from current IP/UDP carrier coordinates used for interoperability. | PARTIAL |
| ADDR-02 | Compatibility carrier | US11799659B2 expressly contemplates coexistence/interoperation with traditional protocols during progressive deployment. | Production v2.2 uses UDP/IP as carrier while logical peer identity is independently registered. | v0.2.0-rc1 MUST retain v2.2 carrier interoperability while evolving logical TEP addressing. | EVIDENCED |
| DISC-01 | Discovery | US11799659B2 uses a distributed database/ledger rather than centralized connection database; EP4169234B1 adds node-list/graph routing concepts. | PeerManager uses blockchain-derived peer registry with peers.json bootstrap/fallback and heartbeat freshness. | TEP-DISCOVERY-v1 MUST define authoritative registry, bootstrap, freshness and failure semantics. | EVIDENCED |
| DISC-02 | Dynamic reachability | EP4169234 family describes network nodes and graph-based selection/routing among nodes. | Authenticated heartbeat may update mutable endpoint coordinates; stale peers expire. | Endpoint changes MUST be accepted only after authenticated observation and MUST NOT redefine stable identity. | EVIDENCED |
| TRANS-01 | Encrypted transport | US11799659B2 requires encryption of transmitted content and transport channels/encapsulation. | Production derives shared keys using X25519 and uses AES-GCM when cryptography is available; APP path requires registered peer key. | TEP-TRANSPORT-v1 MUST preserve authenticated encryption and fail closed for normative secure APP traffic. | EVIDENCED |
| TRANS-02 | Encapsulation | US11799659B2 describes encrypted packet encapsulation and descriptor/relational-hash concepts across network and transport functions. | v2.2 has HBT\x02 magic, version/type, wire node id, nonce, encrypted payload length and HB-TEP-APP/1 envelope. | Freeze the deployed v2 wire format as compatibility profile before defining any v3/native extension. | EVIDENCED |
| TRANS-03 | Routing | US11799659B2 describes direct send where possible and peer-to-peer traversal through intermediate nodes; EP4169234 family covers graph-based routing. | FailoverTepTransport implements direct then approved relay; relay policy is authenticated and constrained. | Discovery/routing MUST support direct path and controlled relay without treating relay coordinates as identity. | EVIDENCED |
| TRANS-04 | Receipt / state transition | US11799659B2 abstract includes encrypted receipt notification and subsequent receiving-node state transition. | APP request/response/error exists, but equivalence to the patented receipt semantics is not yet established. | Do not claim conformance until receipt/state semantics are mapped and tested. | GAP |
| LEDGER-01 | Distributed ledger | US11799659B2 establishes distributed-ledger use for addressing; EP4169233B1 describes distributed ledgers Lx composed of sequential blocks Bn containing transmission records. | Current production exposes blockchain-derived peer discovery but imported TEP modules alone do not establish a native TEP ledger implementation. | TEP-LEDGER-v1 MUST define the TEP ledger separately from public HashBurst/HVM chain and map records to patent semantics. | GAP / DESIGN REQUIRED |
| LEDGER-02 | Block linkage | EP4169233 family describes block header values Hn, previous Hn-1 and increasing count Cn, with body BD containing one or more transmission records rdp. | No verified native implementation in v2.2 imported TEP modules. | Preserve these patent elements in the candidate ledger model; exact serialization/hash domain remains UNFROZEN until claim/description review is complete. | PATENT-EVIDENCED |
| POH-01 | TEP Proof of History | EP4169233 family expressly describes generation of a new ledger block by a proof-of-history protocol to certify temporal order of creation/addition. | No production TEP-PoH implementation has yet been verified in the imported v2.2 modules. | TEP-POH-v1 MUST derive solely from this patent family and project evidence. | PATENT-EVIDENCED / IMPLEMENTATION GAP |
| POH-02 | Hash progression | EP4169233 family states Hn is calculated from Hn-1 and possibly one or more additional values using a hashing algorithm, with an increasing Cn. | No verified production implementation. | Define fH inputs, canonical encoding, counter rules and verification only after exact granted-claim and description trace is completed. | UNFROZEN |
| POH-03 | Temporal ordering | EP4169233B1 ties the PoH procedure to certifying temporal order of block creation/addition. | Heartbeat timestamps/counters in v2.2 transport are transport mechanisms and are NOT evidence of TEP-PoH. | Transport nonce/counter MUST NOT be relabeled as PoH. PoH state is a separate ledger subsystem. | EVIDENCED BOUNDARY |
| POH-04 | Solana exclusion | No cited TEP/BitCorp patent evidence establishes Solana leader schedule, slots, ticks, Solana validator semantics or Solana's specific PoH construction. | Production v2.2 contains no verified Solana PoH subsystem. | TEP-POH-v1 MUST NOT import Solana semantics by analogy. Any similar primitive requires independent patent/project evidence. | NORMATIVE GUARDRAIL |
| GRAPH-01 | Graph routing | EP4169234B1 / IT202000014518A1 / WO2021255633A1 describe secure transmission based on a graph database and node routing/selection. | Production has peer registry, authenticated endpoints, direct/relay behavior; a graph database implementation has not yet been verified in the imported modules. | Model graph routing as a separate discovery/routing layer; do not claim graph-DB conformance until implemented/tested. | PARTIAL / GAP |
| MIG-01 | Legacy coexistence | US11799659B2 contemplates progressive coexistence with traditional network technology/protocols. | Production v2.2 is field-running and byte-identical to the canonical imported baseline. | v0.2.0-rc1 MUST negotiate/preserve v2.2 interoperability; no flag-day replacement. | REQUIRED |
| MIG-02 | Upgrade continuity | Project operational requirement. | Persistent keys/state live outside repository; observer intentionally did not read them. | Installer MUST back up superseded release before switch, preserve identity/state in place, verify hashes and provide rollback. | REQUIRED |

## Explicit non-equivalences

- The transport packet counter and nonce in v2.2 are not TEP-PoH.
- Hash-based logical addressing is not automatically equivalent to the current node_id or peer_id string representation.
- The public HashBurst/HVM blockchain is not automatically the TEP ledger.
- A v2.2 APP response is not automatically the patented encrypted receipt until semantics are traced.
- Peer registry and relay tables are not automatically the patented graph database.
- TEP Proof of History is not Solana Proof of History.

## Freeze gates before normative specifications

1. Complete granted-claim and detailed-description trace for US11799659B2, EP4169233B1 and EP4169234B1.
2. Produce a production-v2.2 wire fixture set without private material.
3. Resolve logical address derivation and ledger record semantics.
4. Resolve exact TEP-PoH fH inputs, block canonicalization, Cn rules, verification and failure/recovery semantics from patent evidence.
5. Define compatibility profile TEP-v2.2 before adding new wire behavior.
6. Only then mark TEP-IDENTITY-v1, TEP-ADDRESS-v1, TEP-DISCOVERY-v1, TEP-TRANSPORT-v1, TEP-LEDGER-v1 and TEP-POH-v1 normative.

## Source references

- https://patents.google.com/patent/US11799659B2/en
- https://patents.google.com/patent/EP4169233B1/en
- https://patents.google.com/patent/EP4169234B1/en
- https://patents.google.com/patent/IT202000014518A1/en
- https://patents.google.com/patent/WO2021255633A1/en
