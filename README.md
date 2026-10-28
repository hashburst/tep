# HashBurst TEP

Canonical repository for the TEP protocol family and runtime.

## Protocol status

**NOT FROZEN.**

This repository is intentionally initialized with a non-normative architecture skeleton only. No document in the initial skeleton defines the patented TEP Ledger or TEP Proof of History mechanism.

The normative protocol will be written only after the patent text and existing deployed TEP implementation have been reconciled.

## Architectural domains to formalize

- TEP logical identity and addressing
- TEP distributed ledger
- TEP-PoH, the proprietary TEP Proof of History mechanism
- local distributed name/address resolution
- peer discovery
- secure transport and bearer abstraction
- routing and forwarding
- P2P
- Federation
- high availability and revocation
- Sovereignty

## Critical distinction

TEP-PoH is a TEP-native mechanism. It must not be documented as Solana Proof of History, as a generic VDF, or as a simple hash chain unless the patent/specification explicitly establishes those semantics.

The TEP Ledger is separate from the public HashBurst blockchain. The exact relationship between TEP Ledger, TEP-PoH, addressing, communication history and any blockchain anchoring remains to be specified from authoritative sources.

## Legacy implementation

The existing `hashburst/node-installer` repository contains deployed HB-TEP code and operational documentation (including HB-TEP-APP/1, X25519/AES-256-GCM transport, discovery/HA and five-node rollout evidence). That implementation is evidence for reconciliation; it is not automatically the normative definition of the patented TEP protocol.

## Planned specification tree

- `docs/architecture/`
- `docs/protocol/addressing/`
- `docs/protocol/ledger/`
- `docs/protocol/poh/`
- `docs/protocol/discovery/`
- `docs/protocol/transport/`
- `docs/protocol/routing/`
- `docs/protocol/federation/`
- `docs/protocol/sovereignty/`
- `schemas/`
- `src/`
- `tests/`

Until protocol freeze, documents under these paths are drafts and must be marked non-normative.
